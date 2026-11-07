"""Descarga herramientas portátiles verificadas; nunca instala software del sistema."""

import argparse
import hashlib
import json
import os
import stat
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".verification/docs-tools"


def extract_verified_zip(archive: Path, destination: Path) -> None:
    """Rechaza rutas fuera del destino y enlaces antes de extraer un solo archivo."""
    root = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            target = (root / entry.filename.replace("\\", "/")).resolve()
            if not target.is_relative_to(root):
                raise ValueError("Ruta de archivo fuera del directorio de herramientas")
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError("No se admiten enlaces simbólicos en herramientas")
        bundle.extractall(root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quarto", action="store_true", help="Añadir Quarto portable Windows"
    )
    args = parser.parse_args()
    versions = json.loads(
        (ROOT / "tools/documentation/versions.json").read_text("utf-8")
    )
    TOOLS.mkdir(parents=True, exist_ok=True)
    names = ["plantuml", "structurizr"]
    if args.quarto:
        if os.name != "nt":
            parser.error(
                "--quarto es el paquete Windows; en CI usar quarto-actions/setup"
            )
        names.append("quarto")
    for name in names:
        info = versions[name]
        asset = TOOLS / info["url"].rsplit("/", 1)[1]
        if not asset.exists():
            request = urllib.request.Request(
                info["url"], headers={"User-Agent": "UniShort-docs"}
            )
            temporary = asset.with_suffix(asset.suffix + ".part")
            with (
                urllib.request.urlopen(request, timeout=120) as response,
                temporary.open("wb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            temporary.replace(asset)
        if hashlib.sha256(asset.read_bytes()).hexdigest() != info["sha256"]:
            raise SystemExit(f"SHA-256 incorrecto: {name}; no se extrae ni ejecuta")
        if asset.suffix == ".zip":
            extract_verified_zip(asset, TOOLS / name)
        print(
            f"{name} {info['version']}: SHA-256 verificado, disponible en .verification/docs-tools"
        )


if __name__ == "__main__":
    main()
