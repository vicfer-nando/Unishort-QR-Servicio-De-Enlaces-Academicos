"""Prueba una copia limpia de fuentes actuales sin .env, .git, venv ni bases reales.

Reutiliza el Python/dependencias instalados: no acredita instalación desde Internet.
No usa git archive porque omitiría los avances locales todavía sin commit.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_sources(destination: Path) -> int:
    """Copia archivos versionados/no ignorados excluyendo datos y secretos locales."""
    output = subprocess.check_output(
        ["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"], cwd=ROOT
    )
    count = 0
    for name in sorted(set(output.decode("utf-8").split("\0"))):
        source = ROOT / name
        if not name or not source.is_file():
            continue
        if source.suffix in {".db", ".sqlite", ".sqlite3", ".pyc"}:
            continue
        if source.name.startswith(".env") and source.name != ".env.example":
            continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        count += 1
    return count


def main() -> None:
    """Ejecuta pytest y JavaScript desde fuentes aisladas; limpia solo su temporal."""
    with tempfile.TemporaryDirectory(prefix="unishort-clean-sources-") as temporary:
        directory = Path(temporary)
        source = directory / "project"
        source.mkdir()
        count = copy_sources(source)
        env = dict(os.environ)
        for name in list(env):
            if name.startswith("UNISHORT_") or name == "PYTHONPATH":
                env.pop(name)
        env["UNISHORT_DATABASE_URL"] = f"sqlite:///{directory.as_posix()}/isolated.db"
        env["UNISHORT_ADMIN_API_KEY"] = ""
        commands = [
            [
                sys.executable,
                "-m",
                "pytest",
                "tests",
                "-p",
                "no:cacheprovider",
                f"--basetemp={directory / 'pytest'}",
                "--tb=short",
            ],
            ["node", "scripts/verify_frontend.mjs"],
            ["node", "--test", "tests/js/admin.test.mjs"],
        ]
        print(
            f"Copia aislada: {count} fuentes; sin BD, .env, .git ni venv.", flush=True
        )
        for command in commands:
            subprocess.run(command, cwd=source, env=env, check=True)
    print("Copia de fuentes verificada; dependencias del entorno actual reutilizadas.")


if __name__ == "__main__":
    main()
