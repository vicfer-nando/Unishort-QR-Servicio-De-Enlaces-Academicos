"""Renderiza modelos formales sin servicios externos ni bases de datos."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".verification/docs-tools"
OUTPUT = ROOT / "quarto/diagrams"


def find_view(exports: Path, key: str) -> Path:
    """Selecciona la vista principal; Structurizr también exporta archivos -key."""
    matches = [
        path
        for path in exports.iterdir()
        if path.suffix in {".puml", ".plantuml"}
        and (path.stem == key or path.stem.endswith("-" + key))
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Exportación Structurizr inesperada para {key}: {len(matches)} vistas"
        )
    return matches[0]


def plantuml(java: str, jar: Path, source: Path, destination: Path) -> None:
    result = subprocess.run(
        [
            java,
            "-Djava.awt.headless=true",
            "-Dfile.encoding=UTF-8",
            "-jar",
            str(jar),
            "-tsvg",
            "-charset",
            "UTF-8",
            "-pipe",
            "-Playout=smetana",
        ],
        input=source.read_bytes(),
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    if b"<svg" not in result.stdout:
        raise RuntimeError(f"PlantUML no produjo SVG: {source.name}")
    visible_text = " ".join(ET.fromstring(result.stdout).itertext())
    if "\ufffd" in visible_text or re.search(
        "[\u00c2\u00c3][\u0080-\u00bf]", visible_text
    ):
        raise ValueError(f"Texto SVG corrupto: comprobar UTF-8 en {source.name}")
    destination.write_bytes(result.stdout)


def main() -> None:
    java = shutil.which("java")
    node = shutil.which("node")
    if not java or not node:
        raise SystemExit(
            "Se requieren Java 17+ y Node 22+; consultar instrucciones-reproduccion.md"
        )
    versions = json.loads(
        (ROOT / "tools/documentation/versions.json").read_text("utf-8")
    )
    jar = TOOLS / versions["plantuml"]["url"].rsplit("/", 1)[1]
    libraries = list((TOOLS / "structurizr").rglob("structurizr-cli*.jar"))
    if not jar.exists() or not libraries:
        raise SystemExit("Ejecutar primero python scripts/setup_docs_tools.py")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    exports = TOOLS / "exports"
    exports.mkdir(exist_ok=True)
    subprocess.run(
        [
            java,
            "-Dfile.encoding=UTF-8",
            "-cp",
            str(libraries[0].parent / "*"),
            "com.structurizr.cli.StructurizrCliApplication",
            "export",
            "-workspace",
            str(ROOT / "docs/arquitectura/unishort-c4.dsl"),
            "-format",
            "plantuml",
            "-output",
            str(exports),
        ],
        cwd=ROOT,
        check=True,
    )
    for key in ("C1-Contexto", "C2-Contenedores", "C3-Componentes-backend"):
        plantuml(java, jar, find_view(exports, key), OUTPUT / f"{key}.svg")
    plantuml(
        java, jar, ROOT / "docs/arquitectura/c4-codigo.puml", OUTPUT / "C4-Codigo.svg"
    )
    env = dict(os.environ)
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(TOOLS / "browsers"))
    subprocess.run(
        [node, "tools/documentation/render-bpmn.mjs"], cwd=ROOT, env=env, check=True
    )
    sources = [
        "docs/arquitectura/unishort-c4.dsl",
        "docs/arquitectura/c4-codigo.puml",
        "docs/procesos/creacion-enlace.bpmn",
    ]
    manifest = {
        "tools": {name: info["version"] for name, info in versions.items()},
        "sources_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in sources
        },
        "svg": sorted(path.name for path in OUTPUT.glob("*.svg")),
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print("Ocho diagramas formales renderizados; manifiesto de fuentes generado.")


if __name__ == "__main__":
    main()
