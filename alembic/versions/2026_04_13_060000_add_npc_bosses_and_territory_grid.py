"""add_npc_bosses_and_territory_grid

Add NPCBoss table and grid_x, grid_y, boss_id columns to Territory.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'npc_bosses_grid'
down_revision: Union[str, None] = 'add_native_pg_enums'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create npc_bosses table
    op.create_table(
        "npc_bosses",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False, server_default=""),
        sa.Column("color", sa.String(16), server_default="#ff4444"),
        sa.Column("influence", sa.Integer(), server_default="10"),
        sa.Column("power", sa.Integer(), server_default="10"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
        ),
    )

    # Add columns to territories
    op.add_column("territories", sa.Column("grid_x", sa.Integer(), server_default="0"))
    op.add_column("territories", sa.Column("grid_y", sa.Integer(), server_default="0"))
    op.add_column(
        "territories",
        sa.Column(
            "boss_id",
            sa.Integer(),
            sa.ForeignKey("npc_bosses.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("territories", "boss_id")
    op.drop_column("territories", "grid_y")
    op.drop_column("territories", "grid_x")
    op.drop_table("npc_bosses")
