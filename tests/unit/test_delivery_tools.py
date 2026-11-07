"""Controles del paquete de entrega: rutas seguras y despliegue deliberado."""

import importlib.util
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "entry", ["../outside.txt", "sub/../../outside.txt", "..\\outside.txt"]
)
def test_tool_archive_rejects_traversal_before_extracting(tmp_path, entry):
    archive = tmp_path / "tools.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("valid.txt", "safe")
        bundle.writestr(entry, "unsafe")
    with pytest.raises(ValueError, match="fuera"):
        load_script("setup_docs_tools").extract_verified_zip(
            archive, tmp_path / "tools"
        )
    assert not (tmp_path / "tools/valid.txt").exists()
    assert not (tmp_path / "outside.txt").exists()


def test_rendered_links_report_missing_files_and_anchors(tmp_path):
    (tmp_path / "index.html").write_text(
        '<a href="other.html#exists">OK</a><img src="missing.svg"><a href="other.html#absent">bad</a>',
        encoding="utf-8",
    )
    (tmp_path / "other.html").write_text('<h1 id="exists">OK</h1>', encoding="utf-8")
    failures = load_script("verify_site").verify_site(tmp_path)
    assert len(failures) == 2
    assert any("missing.svg" in message for message in failures)
    assert any("#absent" in message for message in failures)


def test_dossier_links_stay_navigable_in_generated_site():
    module = load_script("render_portal")
    source = ROOT / "docs/evaluacion/entrega-final/README.md"
    assert (
        module.dossier_link("guion-demostracion.md#recorrido", source)
        == "guion-demostracion.qmd#recorrido"
    )
    assert module.dossier_link("../../../quarto/index.qmd", source) == "../index.qmd"
    assert (
        module.dossier_link("../../../.specify/memory/constitution.md", source)
        == "../sources/constitution.md"
    )
    assert (
        module.dossier_link("https://github.com/example", source)
        == "https://github.com/example"
    )


def test_pages_requires_manual_authorization_and_main():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/documentation.yml").read_text("utf-8")
    )
    # YAML 1.1 interpreta on como booleano; GitHub usa YAML 1.2.
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["workflow_dispatch"]["inputs"]["publicar"]["default"] is False
    deploy = workflow["jobs"]["deploy"]
    assert "github.event_name == 'workflow_dispatch'" in deploy["if"]
    assert "inputs.publicar" in deploy["if"]
    assert "github.ref == 'refs/heads/main'" in deploy["if"]
    assert deploy["needs"] == "build"
    assert workflow["permissions"] == {"contents": "read"}
    assert deploy["permissions"]["pages"] == "write"


def test_structurizr_selects_view_instead_of_its_exported_legend(tmp_path):
    view = tmp_path / "structurizr-C1-Contexto.puml"
    view.write_text("@startuml\n@enduml", encoding="utf-8")
    (tmp_path / "structurizr-C1-Contexto-key.puml").write_text(
        "legend", encoding="utf-8"
    )
    module = load_script("render_diagrams")
    assert module.find_view(tmp_path, "C1-Contexto") == view


def test_quarto_profile_is_scoped_and_does_not_inherit_application_secrets(
    tmp_path, monkeypatch
):
    module = load_script("render_portal")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setenv("UNISHORT_ADMIN_API_KEY", "private-do-not-forward")
    monkeypatch.setenv("UNISHORT_DATABASE_URL", "sqlite:///existing.db")
    environment = module.quarto_environment()
    assert not any(key.startswith("UNISHORT_") for key in environment)
    for key in ("LOCALAPPDATA", "APPDATA", "DENO_DIR", "XDG_CACHE_HOME"):
        assert Path(environment[key]).is_relative_to(tmp_path)
    assert "UNISHORT_ADMIN_API_KEY" in __import__("os").environ


def test_diagram_renderer_rejects_corrupted_accents(tmp_path, monkeypatch):
    from types import SimpleNamespace

    module = load_script("render_diagrams")
    source = tmp_path / "source.puml"
    source.write_text("@startuml\n@enduml", encoding="utf-8")
    bad_svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>Usuario acad\u00c3\u00a9mico</text></svg>'
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=bad_svg.encode("utf-8")),
    )
    with pytest.raises(ValueError, match="UTF-8"):
        module.plantuml("java", tmp_path / "unused.jar", source, tmp_path / "out.svg")
    assert not (tmp_path / "out.svg").exists()
