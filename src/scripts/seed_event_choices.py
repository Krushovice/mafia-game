"""Seed default mission event choices.

Run after migrations:
    export APP_CONFIG__DB__URL='postgresql+asyncpg://...'
    python -m src.scripts.seed_event_choices
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models.enums import EventChoiceType, MissionEventType
from crud.other_crud import mission_crud, mission_event_choice_crud, mission_event_crud


async def seed_event_choices():
    """Create default event choices for police_raid, competitor_attack, random_luck."""
    async with AsyncSession(bind=db_helper.engine) as session:
        # Get existing events
        from sqlalchemy import select

        from core.database.models import MissionEvent

        result = await session.execute(select(MissionEvent))
        events = result.scalars().all()

        event_map = {}
        for ev in events:
            event_map[ev.event_type] = ev.id  # Store ID, not object

        # If events don't exist yet, create them on a sample mission
        if not events:
            # Create a sample mission first
            mission = await mission_crud.create(
                session,
                {
                    "name": "Seed Mission",
                    "description": "Auto-created for event seeding",
                    "duration": 60,
                    "reward_money": 0,
                    "reward_influence": 0,
                    "difficulty": "easy",
                    "mission_stat_type": "force",
                    "slots": 1,
                    "power_required": 5,
                    "intellect_required": 0,
                    "agility_required": 0,
                },
            )
            await session.flush()  # Get ID without commit
            mission_id = mission.id

            # Create events
            for et in MissionEventType:
                ev_data = {
                    "mission_id": mission_id,
                    "event_type": et,
                    "chance": 10,
                    "description": {
                        MissionEventType.POLICE_RAID: "🚔 Облава полиции! Копи нагрянули на вашу операцию.",
                        MissionEventType.COMPETITOR_ATTACK: "⚔️ Конкуренты атакуют! Вражеская банда вышла на ваши следы.",
                        MissionEventType.RANDOM_LUCK: "🍀 Удача улыбнулась! Внезапный бонус.",
                    }[et],
                    "parameters": {},
                    "order": list(MissionEventType).index(et),
                }
                ev = await mission_event_crud.create(session, ev_data)
                await session.flush()
                event_map[et] = ev

            await session.commit()

        # Define default choices for each event type
        choices_data = {
            MissionEventType.POLICE_RAID: [
                {
                    "choice_type": EventChoiceType.PAYOFF,
                    "label": "💰 Откупиться",
                    "description": "Дать взятку. Потеря денег, но миссия продолжится.",
                    "money_cost": 200,
                    "influence_required": 0,
                    "power_required": 0,
                    "success_chance_base": 100,
                },
                {
                    "choice_type": EventChoiceType.TALK,
                    "label": "🗣️ Заговорить зубы",
                    "description": "Использовать связи и влияние. Шанс зависит от влияния.",
                    "money_cost": 0,
                    "influence_required": 10,
                    "power_required": 0,
                    "success_chance_base": 50,
                },
                {
                    "choice_type": EventChoiceType.DO_NOTHING,
                    "label": "😶 Бездействие",
                    "description": "Ничего не делать. Миссия провалена, -5 влияния.",
                    "money_cost": 0,
                    "influence_required": 0,
                    "power_required": 0,
                    "success_chance_base": 0,
                },
            ],
            MissionEventType.COMPETITOR_ATTACK: [
                {
                    "choice_type": EventChoiceType.FIGHT,
                    "label": "⚔️ В бой",
                    "description": "Отбить атаку. Зависит от силы и оружия.",
                    "money_cost": 0,
                    "influence_required": 5,
                    "power_required": 10,
                    "success_chance_base": 60,
                },
                {
                    "choice_type": EventChoiceType.PAYOFF,
                    "label": "💰 Откупиться",
                    "description": "Заплатить конкурентам. Потеря денег.",
                    "money_cost": 300,
                    "influence_required": 0,
                    "power_required": 0,
                    "success_chance_base": 100,
                },
                {
                    "choice_type": EventChoiceType.DO_NOTHING,
                    "label": "😶 Бездействие",
                    "description": "Ничего не делать. Миссия провалена.",
                    "money_cost": 0,
                    "influence_required": 0,
                    "power_required": 0,
                    "success_chance_base": 0,
                },
            ],
            MissionEventType.RANDOM_LUCK: [
                {
                    "choice_type": EventChoiceType.DO_NOTHING,
                    "label": "✨ Принять удачу",
                    "description": "Автоматический бонус к награде.",
                    "money_cost": 0,
                    "influence_required": 0,
                    "power_required": 0,
                    "success_chance_base": 100,
                },
            ],
        }

        # Create choices
        created = 0
        for event_type, choices in choices_data.items():
            event_id = event_map.get(event_type)
            if not event_id:
                print(f"  ⚠️  Event {event_type.value} not found, skipping")
                continue

            for ch in choices:
                ch["event_id"] = event_id
                await mission_event_choice_crud.create(session, ch)
                created += 1

        await session.commit()
        return created


async def main():
    print("🌱 Seeding mission event choices...")
    count = await seed_event_choices()
    print(f"✅ Created {count} event choices")
    await db_helper.engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
