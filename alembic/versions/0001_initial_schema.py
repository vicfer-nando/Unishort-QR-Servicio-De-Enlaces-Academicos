"""Esquema base de enlaces cortos.

Revision ID: 0001
Revises:
Create Date: 2026-11-05
"""

from __future__ import annotations

import os
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "short_urls"


def _columns(inspector: sa.Inspector) -> set[str]:
    return {column["name"] for column in inspector.get_columns(TABLE)}


def _indexes(inspector: sa.Inspector) -> set[str]:
    return {
        index["name"]
        for index in inspector.get_indexes(TABLE)
        if index["name"] is not None
    }


def upgrade() -> None:
    """Crea o completa el esquema sin perder los enlaces existentes."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if TABLE not in inspector.get_table_names():
        op.create_table(
            TABLE,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("short_code", sa.String(length=16), nullable=False),
            sa.Column("original_url", sa.String(length=2048), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            ),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "click_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = sa.inspect(bind)

    columns = _columns(inspector)
    if "is_active" not in columns:
        op.add_column(
            TABLE,
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            ),
        )
    if "expires_at" not in columns:
        op.add_column(
            TABLE, sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)
        )
    if "click_count" not in columns:
        op.add_column(
            TABLE,
            sa.Column(
                "click_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )

    inspector = sa.inspect(bind)
    indexes = _indexes(inspector)
    if "ix_short_urls_id" not in indexes:
        op.create_index("ix_short_urls_id", TABLE, ["id"], unique=False)
    if "ix_short_urls_short_code" not in indexes:
        op.create_index("ix_short_urls_short_code", TABLE, ["short_code"], unique=True)
    if "ix_short_urls_expires_at" not in indexes:
        op.create_index("ix_short_urls_expires_at", TABLE, ["expires_at"], unique=False)


def downgrade() -> None:
    """Elimina el esquema solo con autorización explícita."""

    if os.getenv("UNISHORT_ALEMBIC_ALLOW_DESTRUCTIVE_DOWNGRADE") != "1":
        raise RuntimeError(
            "El downgrade elimina datos. Defina "
            "UNISHORT_ALEMBIC_ALLOW_DESTRUCTIVE_DOWNGRADE=1 para confirmarlo."
        )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if TABLE not in inspector.get_table_names():
        return

    indexes = _indexes(inspector)
    for name in (
        "ix_short_urls_expires_at",
        "ix_short_urls_short_code",
        "ix_short_urls_id",
    ):
        if name in indexes:
            op.drop_index(name, table_name=TABLE)
    op.drop_table(TABLE)
