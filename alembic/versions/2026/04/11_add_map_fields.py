"""add map fields to user missions

Revision ID: add_map_fields
Revises: 85b8255de087
Create Date: 2026-04-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "add_map_fields"
down_revision = "85b8255de087"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_missions",
        sa.Column(
            "available_until",
            sa.DateTime(),
            nullable=True,
        ),
    )
    op.add_column(
        "user_missions",
        sa.Column("location_name", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "user_missions",
        sa.Column("position_x", sa.Integer(), nullable=True),
    )
    op.add_column(
        "user_missions",
        sa.Column("position_y", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_missions", "position_y")
    op.drop_column("user_missions", "position_x")
    op.drop_column("user_missions", "location_name")
    op.drop_column("user_missions", "available_until")
