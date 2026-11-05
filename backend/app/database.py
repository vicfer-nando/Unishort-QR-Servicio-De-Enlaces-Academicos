"""Conexión, sesión y evolución aditiva del esquema de datos.

Se conserva la base SQLite existente. Las columnas nuevas se agregan con
``ALTER TABLE ADD COLUMN`` idempotente para no recrear ni perder datos.
"""

from typing import Generator

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False}
    if _settings.database_url.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base declarativa tipada de SQLAlchemy 2.0."""


_ADDITIVE_COLUMNS: dict[str, str] = {
    "is_active": "BOOLEAN NOT NULL DEFAULT 1",
    "expires_at": "DATETIME",
    "click_count": "INTEGER NOT NULL DEFAULT 0",
}

_ADDITIVE_INDEXES: dict[str, str] = {
    "ix_short_urls_created_at": "CREATE INDEX IF NOT EXISTS ix_short_urls_created_at "
    "ON short_urls (created_at)",
    "ix_short_urls_expires_at": "CREATE INDEX IF NOT EXISTS ix_short_urls_expires_at "
    "ON short_urls (expires_at)",
    "ix_short_urls_is_active": "CREATE INDEX IF NOT EXISTS ix_short_urls_is_active "
    "ON short_urls (is_active)",
}


def ensure_schema(bind: Engine = engine) -> None:
    """Agrega columnas e índices faltantes sin recrear la tabla existente.

    Parameters
    ----------
    bind:
        Motor de SQLAlchemy sobre el que se inspecciona y evoluciona el esquema.

    Notes
    -----
    Esta función es idempotente. Solo añade lo que falta; nunca elimina tablas,
    columnas ni filas. Se ejecuta al arrancar para mantener compatibles las
    bases de datos creadas por versiones anteriores del proyecto.
    """

    inspector = inspect(bind)
    if "short_urls" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("short_urls")}
    with bind.begin() as connection:
        for column_name, column_definition in _ADDITIVE_COLUMNS.items():
            if column_name not in existing:
                connection.execute(
                    text(
                        f"ALTER TABLE short_urls ADD COLUMN {column_name} {column_definition}"
                    )
                )
        if bind.dialect.name == "sqlite":
            for statement in _ADDITIVE_INDEXES.values():
                connection.execute(text(statement))


def get_db() -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos por petición.

    Yields
    ------
    Session
        Sesión de SQLAlchemy que se cierra de forma garantizada al terminar.
    """

    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
