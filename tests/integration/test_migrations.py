"""Pruebas de adopción y aplicación de las migraciones de Alembic."""

import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[2]


def _config(database_path: Path, monkeypatch) -> Config:
    monkeypatch.setenv("UNISHORT_DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "alembic"))
    return config


def _create_legacy_database(database_path: Path) -> None:
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE short_urls (
                id INTEGER NOT NULL,
                short_code VARCHAR NOT NULL,
                original_url VARCHAR NOT NULL,
                created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                PRIMARY KEY (id)
            );
            CREATE UNIQUE INDEX ix_short_urls_short_code
                ON short_urls (short_code);
            CREATE INDEX ix_short_urls_id ON short_urls (id);
            INSERT INTO short_urls (short_code, original_url)
                VALUES ('legacy1', 'https://example.edu/legado');
            """
        )
        connection.commit()
    finally:
        connection.close()


def _inspect(database_path: Path):
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        return inspect(engine)
    finally:
        engine.dispose()


def test_upgrade_adopts_legacy_database_without_losing_rows(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy.db"
    _create_legacy_database(database_path)

    command.upgrade(_config(database_path, monkeypatch), "head")

    inspector = _inspect(database_path)
    columns = {column["name"] for column in inspector.get_columns("short_urls")}
    indexes = {
        index["name"] for index in inspector.get_indexes("short_urls") if index["name"]
    }

    assert {"is_active", "expires_at", "click_count"} <= columns
    assert "ix_short_urls_created_at" in indexes
    assert "ix_short_urls_expires_at" in indexes

    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(
            "SELECT short_code, original_url, is_active, click_count "
            "FROM short_urls WHERE short_code = 'legacy1'"
        ).fetchone()
        version = connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone()
    finally:
        connection.close()

    assert row == ("legacy1", "https://example.edu/legado", 1, 0)
    assert version == ("0003",)


def test_upgrade_creates_complete_fresh_database(tmp_path, monkeypatch):
    database_path = tmp_path / "fresh.db"

    command.upgrade(_config(database_path, monkeypatch), "head")

    inspector = _inspect(database_path)
    columns = {column["name"] for column in inspector.get_columns("short_urls")}

    assert {
        "id",
        "short_code",
        "original_url",
        "created_at",
        "is_active",
        "expires_at",
        "click_count",
    } == columns

    from app.database import Base

    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.connect() as connection:
            assert (
                compare_metadata(MigrationContext.configure(connection), Base.metadata)
                == []
            )
    finally:
        engine.dispose()


def test_downgrade_requires_explicit_destructive_confirmation(tmp_path, monkeypatch):
    database_path = tmp_path / "guarded.db"
    config = _config(database_path, monkeypatch)
    command.upgrade(config, "head")

    monkeypatch.delenv("UNISHORT_ALEMBIC_ALLOW_DESTRUCTIVE_DOWNGRADE", raising=False)
    with pytest.raises(
        RuntimeError, match="UNISHORT_ALEMBIC_ALLOW_DESTRUCTIVE_DOWNGRADE"
    ):
        command.downgrade(config, "base")

    assert "short_urls" in _inspect(database_path).get_table_names()

    monkeypatch.setenv("UNISHORT_ALEMBIC_ALLOW_DESTRUCTIVE_DOWNGRADE", "1")
    command.downgrade(config, "base")

    assert "short_urls" not in _inspect(database_path).get_table_names()
