"""Valida UTF-8, enlaces locales, YAML y referencias BPMN sin afirmar render."""

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Revisa fuentes públicas; exige preparar recursos Quarto previamente."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-unrendered-diagrams", action="store_true")
    args = parser.parse_args()
    expected_diagrams = {
        "C1-Contexto.svg",
        "C2-Contenedores.svg",
        "C3-Componentes-backend.svg",
        "C4-Codigo.svg",
        "bpmn-Diagram_Create.svg",
        "bpmn-Diagram_QR.svg",
        "bpmn-Diagram_Redirect.svg",
        "bpmn-Diagram_Admin.svg",
        "manifest.json",
    }
    files = [ROOT / "README.md", ROOT / ".specify/memory/constitution.md"]
    for directory in ("docs", "specs", "quarto"):
        files.extend(
            path
            for path in (ROOT / directory).rglob("*")
            if path.is_file()
            and path.suffix in {".md", ".qmd", ".yml", ".bpmn", ".dsl", ".puml"}
            and not any(part in {"sources", "_site", ".quarto"} for part in path.parts)
        )
    broken = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="strict")
        assert "\ufffd" not in text, path
        for line in text.splitlines():
            if "http" not in line:
                assert not re.search(r"[A-Za-z]\?[A-Za-z]", line), (path, line)
        if path.suffix in {".md", ".qmd"}:
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if link.startswith(("http:", "https:", "#", "mailto:")):
                    continue
                target = unquote(link.split("#")[0])
                if target and not (path.parent / target).exists():
                    resolved = (path.parent / target).resolve()
                    allowed = (
                        args.allow_unrendered_diagrams
                        and resolved.parent == (ROOT / "quarto/diagrams").resolve()
                        and resolved.name in expected_diagrams
                    )
                    if not allowed:
                        broken.append(f"{path.relative_to(ROOT)} -> {link}")
    if broken:
        raise SystemExit("Enlaces locales inexistentes:\n" + "\n".join(broken))
    xml = ET.parse(ROOT / "docs/procesos/creacion-enlace.bpmn")
    elements = list(xml.iter())
    identifiers = [
        element.attrib["id"] for element in elements if "id" in element.attrib
    ]
    assert len(identifiers) == len(set(identifiers))
    ids = set(identifiers)
    for element in elements:
        for attribute in ("sourceRef", "targetRef", "processRef", "bpmnElement"):
            if attribute in element.attrib:
                assert element.attrib[attribute] in ids
        if element.tag.rsplit("}", 1)[-1] in {"flowNodeRef", "incoming", "outgoing"}:
            assert element.text.strip() in ids
    for path in (
        ROOT / "quarto/_quarto.yml",
        ROOT / "docker-compose.yml",
        ROOT / ".github/workflows/quality.yml",
        ROOT / ".github/workflows/documentation.yml",
    ):
        assert isinstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict)
    print(
        f"UTF-8 y enlaces: {len(files)} fuentes OK; YAML OK; BPMN XML y referencias OK."
    )
    print(
        "No equivale a render Quarto/PlantUML/Structurizr ni validación BPMN por XSD."
    )
    if args.allow_unrendered_diagrams:
        print(
            "Modo fuentes: existencia de los nueve derivados de diagramas no exigida."
        )


if __name__ == "__main__":
    main()
