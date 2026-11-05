"""Índice para ordenar enlaces por fecha de creación.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-05
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "short_urls"
INDEX = "ix_short_urls_created_at"


def upgrade() -> None:
    """Crea el índice de ``created_at`` si todavía no existe."""

    inspector = sa.inspect(op.get_bind())
    indexes = {
        index["name"]
        for index in inspector.get_indexes(TABLE)
        if index["name"] is not None
    }
    if INDEX not in indexes:
        op.create_index(INDEX, TABLE, ["created_at"], unique=False)


def downgrade() -> None:
    """Elimina únicamente el índice, sin tocar los datos."""

    inspector = sa.inspect(op.get_bind())
    indexes = {
        index["name"]
        for index in inspector.get_indexes(TABLE)
        if index["name"] is not None
    }
    if INDEX in indexes:
        op.drop_index(INDEX, table_name=TABLE)
