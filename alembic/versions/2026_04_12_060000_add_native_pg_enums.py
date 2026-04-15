"""add_native_pg_enums

Convert varchar columns to native PostgreSQL enum types.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_native_pg_enums"
down_revision: Union[str, None] = "f6a282f6fff3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём все enum типы
    op.execute(
        "CREATE TYPE characterrole AS ENUM ('thug', 'hacker', 'negotiator', 'capo')"
    )
    op.execute("CREATE TYPE charactertrait AS ENUM ('hot', 'quiet', 'greedy')")
    op.execute("CREATE TYPE missiondifficulty AS ENUM ('easy', 'medium', 'hard')")
    op.execute("CREATE TYPE missionstattype AS ENUM ('force', 'stealth', 'diplomacy')")
    op.execute(
        "CREATE TYPE territorytype AS ENUM ('district', 'neighborhood', 'borough')"
    )
    op.execute(
        "CREATE TYPE missionstatus AS ENUM ("
        "'pending', 'in_progress', 'waiting_event', 'success', 'completed', 'failed'"
        ")"
    )
    op.execute(
        "CREATE TYPE eventchoicetype AS ENUM ('payoff', 'fight', 'talk', 'do_nothing')"
    )
    op.execute("CREATE TYPE shopitemtype AS ENUM ('character', 'weapon', 'tool')")

    # Преобразуем varchar → enum
    # Сначала убираем server_default, потом конвертируем, потом возвращаем

    # Missions
    op.execute("ALTER TABLE missions ALTER COLUMN difficulty DROP DEFAULT")
    op.execute("ALTER TABLE missions ALTER COLUMN mission_stat_type DROP DEFAULT")
    op.execute("ALTER TABLE user_missions ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE territories ALTER COLUMN territory_type DROP DEFAULT")
    op.execute("ALTER TABLE characters ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE characters ALTER COLUMN trait DROP DEFAULT")
    op.execute("ALTER TABLE shop_items ALTER COLUMN item_type DROP DEFAULT")

    # Characters
    op.execute(
        "ALTER TABLE characters ALTER COLUMN role TYPE characterrole USING lower(role)::characterrole"
    )
    op.execute(
        "ALTER TABLE characters ALTER COLUMN trait TYPE charactertrait USING lower(trait)::charactertrait"
    )

    # Missions
    op.execute(
        "ALTER TABLE missions ALTER COLUMN difficulty TYPE missiondifficulty USING lower(difficulty)::missiondifficulty"
    )
    op.execute("ALTER TABLE missions ALTER COLUMN difficulty SET DEFAULT 'easy'")
    op.execute(
        "ALTER TABLE missions ALTER COLUMN mission_stat_type TYPE missionstattype USING lower(mission_stat_type)::missionstattype"
    )
    op.execute(
        "ALTER TABLE missions ALTER COLUMN mission_stat_type SET DEFAULT 'force'"
    )

    # Shop items
    op.execute(
        "ALTER TABLE shop_items ALTER COLUMN item_type TYPE shopitemtype USING lower(item_type)::shopitemtype"
    )
    op.execute(
        "ALTER TABLE shop_items ALTER COLUMN role TYPE characterrole USING lower(role)::characterrole"
    )
    op.execute(
        "ALTER TABLE shop_items ALTER COLUMN trait TYPE charactertrait USING lower(trait)::charactertrait"
    )

    # Territory
    op.execute(
        "ALTER TABLE territories ALTER COLUMN territory_type TYPE territorytype USING lower(territory_type)::territorytype"
    )
    op.execute(
        "ALTER TABLE territories ALTER COLUMN territory_type SET DEFAULT 'district'"
    )

    # Characters defaults
    op.execute("ALTER TABLE characters ALTER COLUMN role SET DEFAULT 'thug'")
    op.execute("ALTER TABLE characters ALTER COLUMN trait SET DEFAULT 'quiet'")

    # Shop items defaults
    op.execute("ALTER TABLE shop_items ALTER COLUMN item_type SET DEFAULT 'character'")

    # User missions
    op.execute(
        "ALTER TABLE user_missions ALTER COLUMN status TYPE missionstatus USING lower(status)::missionstatus"
    )
    op.execute("ALTER TABLE user_missions ALTER COLUMN status SET DEFAULT 'pending'")

    # Mission event choices
    op.execute(
        "ALTER TABLE mission_event_choices ALTER COLUMN choice_type TYPE eventchoicetype USING lower(choice_type)::eventchoicetype"
    )

    # User mission event logs
    op.execute(
        "ALTER TABLE user_mission_event_logs ALTER COLUMN chosen_type TYPE eventchoicetype USING lower(chosen_type)::eventchoicetype"
    )


def downgrade() -> None:
    # Преобразуем обратно в varchar
    op.execute(
        "ALTER TABLE characters ALTER COLUMN role TYPE varchar(32) USING role::text"
    )
    op.execute(
        "ALTER TABLE characters ALTER COLUMN trait TYPE varchar(32) USING trait::text"
    )
    op.execute(
        "ALTER TABLE missions ALTER COLUMN difficulty TYPE varchar(32) USING difficulty::text"
    )
    op.execute(
        "ALTER TABLE missions ALTER COLUMN mission_stat_type TYPE varchar(32) USING mission_stat_type::text"
    )
    op.execute(
        "ALTER TABLE shop_items ALTER COLUMN item_type TYPE varchar(32) USING item_type::text"
    )
    op.execute(
        "ALTER TABLE shop_items ALTER COLUMN role TYPE varchar(32) USING role::text"
    )
    op.execute(
        "ALTER TABLE shop_items ALTER COLUMN trait TYPE varchar(32) USING trait::text"
    )
    op.execute(
        "ALTER TABLE territories ALTER COLUMN territory_type TYPE varchar(32) USING territory_type::text"
    )
    op.execute(
        "ALTER TABLE user_missions ALTER COLUMN status TYPE varchar(32) USING status::text"
    )
    op.execute(
        "ALTER TABLE mission_event_choices ALTER COLUMN choice_type TYPE varchar(32) USING choice_type::text"
    )
    op.execute(
        "ALTER TABLE user_mission_event_logs ALTER COLUMN chosen_type TYPE varchar(32) USING chosen_type::text"
    )

    # Удаляем enum типы
    op.execute("DROP TYPE characterrole")
    op.execute("DROP TYPE charactertrait")
    op.execute("DROP TYPE missiondifficulty")
    op.execute("DROP TYPE missionstattype")
    op.execute("DROP TYPE territorytype")
    op.execute("DROP TYPE missionstatus")
    op.execute("DROP TYPE eventchoicetype")
    op.execute("DROP TYPE shopitemtype")
