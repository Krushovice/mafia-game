"""add_notifications_table

Adds the `notifications` table — Telegram notification queue. API/background-tasks
write pending rows; the bot dispatcher polls and sends them.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "notifications_queue"
down_revision: Union[str, None] = "npc_bosses_grid"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE notificationtype AS ENUM ("
        "'mission_completed', 'mission_failed', 'mission_event', "
        "'flash_mission', 'raid', 'generic'"
        ")"
    )
    op.execute(
        "CREATE TYPE notificationstatus AS ENUM ('pending', 'sent', 'failed')"
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "notification_type",
            sa.Enum(
                "mission_completed",
                "mission_failed",
                "mission_event",
                "flash_mission",
                "raid",
                "generic",
                name="notificationtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "sent",
                "failed",
                name="notificationstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_notifications_user_id", "notifications", ["user_id"]
    )
    op.create_index(
        "ix_notifications_status", "notifications", ["status"]
    )
    op.create_index(
        "ix_notifications_created_at", "notifications", ["created_at"]
    )
    op.create_index(
        "ix_notifications_status_created_at",
        "notifications",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_status_created_at", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_status", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.execute("DROP TYPE notificationstatus")
    op.execute("DROP TYPE notificationtype")
