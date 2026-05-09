"""Add mission_type to user_missions, make user_id nullable for global flash missions."""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "flash_mission_type"
down_revision: Union[str, None] = "daily_quests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE missiontype AS ENUM ('regular', 'flash', 'territory', 'return')"
    )

    op.add_column(
        "user_missions",
        sa.Column(
            "mission_type",
            sa.Enum(
                "regular",
                "flash",
                "territory",
                "return",
                name="missiontype",
                create_type=False,
            ),
            nullable=True,
            server_default="regular",
        ),
    )

    op.execute(
        "UPDATE user_missions SET mission_type = 'regular' WHERE mission_type IS NULL"
    )

    # user_id nullable — global flash missions exist without a specific owner
    op.alter_column("user_missions", "user_id", nullable=True)


def downgrade() -> None:
    op.execute(
        "UPDATE user_missions SET user_id = 0 WHERE user_id IS NULL"
    )
    op.alter_column("user_missions", "user_id", nullable=False)
    op.drop_column("user_missions", "mission_type")
    op.execute("DROP TYPE missiontype")
