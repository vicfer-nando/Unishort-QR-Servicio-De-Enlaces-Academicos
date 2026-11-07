"""Prepara fuentes enlazadas del portal y renderiza con Quarto si está instalado."""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def dossier_link(link: str, source: Path, root: Path = ROOT) -> str:
    """Convierte enlaces del dossier canónico en destinos válidos dentro del sitio."""
    if link.startswith(("https:", "http:", "mailto:", "#")):
        return link
    target, separator, anchor = link.partition("#")
    resolved = (source.parent / unquote(target)).resolve()
    relative = resolved.relative_to(root.resolve())
    dossier = Path("docs/evaluacion/entrega-final")
    if relative.as_posix() == ".specify/memory/constitution.md":
        result = "../sources/constitution.md"
    elif relative.parts[:2] == (".github", "workflows"):
        result = "../sources/workflows/" + relative.name
    elif relative.parent == dossier and relative.suffix == ".md":
        result = relative.with_suffix(".qmd").name
    elif relative.parts[0] == "quarto":
        result = "../" + Path(*relative.parts[1:]).as_posix()
    else:
        result = "../sources/" + relative.as_posix()
    return result + (separator + anchor if separator else "")


def prepare_dossier() -> None:
    destination = ROOT / "quarto/paquete"
    destination.mkdir(exist_ok=True)
    for source in (ROOT / "docs/evaluacion/entrega-final").glob("*.md"):
        content = source.read_text("utf-8")
        heading, _, body = content.partition("\n")
        title = heading.removeprefix("# ").replace('"', '\\"')
        body = re.sub(
            r"(?<=\]\()([^\)]+)(?=\))",
            lambda match: dossier_link(match[1], source),
            body,
        )
        (destination / source.with_suffix(".qmd").name).write_text(
            f'---\ntitle: "{title}"\n---\n\n{body.lstrip()}', encoding="utf-8"
        )


def find_quarto() -> str | None:
    configured = os.environ.get("QUARTO_BIN")
    if configured:
        return configured
    installed = shutil.which("quarto")
    if installed:
        return installed
    portable = ROOT / ".verification/docs-tools/quarto"
    for name in ("quarto.exe", "quarto.cmd", "quarto"):
        for candidate in portable.rglob(name):
            if candidate.parent.name == "bin":
                return str(candidate)
    return None


def quarto_environment() -> dict[str, str]:
    """Aísla cachés del render y no reenvía secretos/configuración del producto."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("UNISHORT_")
    }
    profile = ROOT / ".verification/quarto-profile"
    for key, directory in {
        "LOCALAPPDATA": "local",
        "APPDATA": "roaming",
        "DENO_DIR": "deno",
        "XDG_CACHE_HOME": "cache",
        "XDG_DATA_HOME": "data",
        "XDG_RUNTIME_DIR": "runtime",
    }.items():
        target = profile / directory
        target.mkdir(parents=True, exist_ok=True)
        environment[key] = str(target)
    return environment


def export_openapi(destination: Path) -> None:
    """Genera el esquema real en un subproceso con SQLite temporal y sin clave."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("UNISHORT_")
    }
    with tempfile.TemporaryDirectory(prefix="unishort-openapi-") as temporary:
        env.update(
            UNISHORT_DATABASE_URL=f"sqlite:///{Path(temporary).as_posix()}/schema.db",
            UNISHORT_ADMIN_API_KEY="",
            UNISHORT_BASE_URL="http://localhost:8000",
            UNISHORT_API_PREFIX="/api/v1",
        )
        command = (
            "import json; from backend.app.main import app; "
            "from backend.app.database import engine; "
            "print(json.dumps(app.openapi(), ensure_ascii=True, indent=2)); engine.dispose()"
        )
        with destination.open("w", encoding="utf-8") as output:
            subprocess.run(
                [sys.executable, "-c", command],
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.PIPE,
                check=True,
            )


def main():
    """Copia documentación pública a un directorio generado, sin tocar originales."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    destination = ROOT / "quarto" / "sources"
    destination.mkdir(exist_ok=True)
    for directory in ("docs", "specs"):
        shutil.copytree(ROOT / directory, destination / directory, dirs_exist_ok=True)
    shutil.copy2(ROOT / "README.md", destination / "README.md")
    shutil.copy2(
        ROOT / ".specify/memory/constitution.md", destination / "constitution.md"
    )
    workflows = destination / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    for source in (ROOT / ".github/workflows").glob("*.yml"):
        shutil.copy2(source, workflows / source.name)
    official_pdf = ROOT / "Asignación_Y_Rubrica_Evaluación_Sumativa_1.pdf"
    if official_pdf.exists():
        shutil.copy2(official_pdf, destination / official_pdf.name)
    export_openapi(destination / "openapi.json")
    prepare_dossier()
    print("Fuentes públicas preparadas en quarto/sources; originales intactos.")
    if args.prepare_only:
        return
    executable = find_quarto()
    if executable is None:
        raise SystemExit(
            "Quarto no está disponible. Instálelo y repita python scripts/render_portal.py"
        )
    subprocess.run(
        [executable, "render", str(ROOT / "quarto")],
        cwd=ROOT,
        env=quarto_environment(),
        check=True,
    )


if __name__ == "__main__":
    main()
