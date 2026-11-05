"""Entorno de migraciones de UniShort QR.

La URL se toma de ``UNISHORT_DATABASE_URL`` (o del valor por defecto de la
configuración) para que Alembic y la aplicación usen siempre la misma base de
datos. No se ejecutan operaciones destructivas al adoptar una base existente.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import models  # noqa: E402, F401
from app.config import Settings  # noqa: E402
from app.database import Base  # noqa: E402

config = context.config

settings = Settings()
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta las migraciones sin abrir una conexión real."""

    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta las migraciones sobre una conexión real."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
