"""Alinea el índice de estado con ORM y arranque heredado, sin tocar filas."""

import sqlalchemy as sa

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

INDEX = "ix_short_urls_is_active"


def upgrade() -> None:
    """Agrega únicamente el índice si la base todavía no lo tiene."""

    indexes = {
        index["name"] for index in sa.inspect(op.get_bind()).get_indexes("short_urls")
    }
    if INDEX not in indexes:
        op.create_index(INDEX, "short_urls", ["is_active"], unique=False)


def downgrade() -> None:
    """Retira el índice de esta revisión sin eliminar registros."""

    op.drop_index(INDEX, table_name="short_urls")
