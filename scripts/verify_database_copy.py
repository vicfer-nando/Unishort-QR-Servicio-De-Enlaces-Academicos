"""Migra solo una copia temporal de unishort.db y comprueba filas y hash."""

import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Lee el original en modo solo lectura; compara sin imprimir sus URLs."""
    source = ROOT / "unishort.db"
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="unishort-migration-copy-") as temporary:
        copy = Path(temporary) / "copy.db"
        original = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
        target = sqlite3.connect(copy)
        try:
            original.backup(target)
            columns = [
                column[1]
                for column in original.execute("PRAGMA table_info(short_urls)")
            ]
            assert set(columns) <= {
                "id",
                "short_code",
                "original_url",
                "created_at",
                "is_active",
                "expires_at",
                "click_count",
            }
            before = original.execute("SELECT * FROM short_urls ORDER BY id").fetchall()
        finally:
            target.close()
            original.close()
        env = dict(os.environ, UNISHORT_DATABASE_URL=f"sqlite:///{copy.as_posix()}")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env=env,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError("No se pudo migrar la copia temporal")
        migrated = sqlite3.connect(copy)
        try:
            fields = ", ".join(f'"{column}"' for column in columns)
            after = migrated.execute(
                f"SELECT {fields} FROM short_urls ORDER BY id"
            ).fetchall()
            assert before == after
            assert migrated.execute("PRAGMA integrity_check").fetchone() == ("ok",)
            version = migrated.execute(
                "SELECT version_num FROM alembic_version"
            ).fetchone()[0]
        finally:
            migrated.close()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    print(
        f"Copia migrada a {version}; {len(before)} registros conservados; integridad OK."
    )
    print(f"SHA256 original intacto: {original_hash}")


if __name__ == "__main__":
    main()
