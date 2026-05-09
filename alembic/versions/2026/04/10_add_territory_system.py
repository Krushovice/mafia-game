"""add_territory_system

Revision ID: add_territory_system
Revises: 606f7e731343
Create Date: 2026-04-10
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_territory_system"
down_revision = "606f7e731343"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create territories table
    op.create_table(
        "territories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(length=64),
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "territory_type",
            sa.String(length=32),
            nullable=False,
            server_default="district",
        ),
        sa.Column(
            "description",
            sa.String(length=256),
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "influence_required",
            sa.Integer(),
            nullable=False,
            server_default="25",
        ),
        sa.Column(
            "power_required",
            sa.Integer(),
            nullable=False,
            server_default="20",
        ),
        sa.Column(
            "intellect_required",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),
        sa.Column(
            "agility_required",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),
        sa.Column(
            "reward_influence",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),
        sa.Column(
            "reward_money",
            sa.Integer(),
            nullable=False,
            server_default="200",
        ),
        sa.Column(
            "passive_income_money",
            sa.Integer(),
            nullable=False,
            server_default="50",
        ),
        sa.Column(
            "passive_income_influence",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create user_territories table
    op.create_table(
        "user_territories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("territory_id", sa.Integer(), nullable=False),
        sa.Column(
            "captured_at",
            sa.DateTime(),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["territory_id"],
            ["territories.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_territories_user_id",
        "user_territories",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_territories_territory_id",
        "user_territories",
        ["territory_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_territories_territory_id",
        table_name="user_territories",
    )
    op.drop_index("ix_user_territories_user_id", table_name="user_territories")
    op.drop_table("user_territories")
    op.drop_table("territories")
