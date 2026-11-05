"""Prepara fuentes enlazadas del portal y renderiza con Quarto si está instalado."""

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    print("Fuentes públicas preparadas en quarto/sources; originales intactos.")
    if args.prepare_only:
        return
    executable = shutil.which("quarto")
    if executable is None:
        raise SystemExit(
            "Quarto no está disponible. Instálelo y repita python scripts/render_portal.py"
        )
    subprocess.run([executable, "render", str(ROOT / "quarto")], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
