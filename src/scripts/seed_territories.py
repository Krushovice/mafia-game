"""Seed 8 default territories."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models.enums import TerritoryType
from crud.other_crud import territory_crud


TERRITORIES = [
    {
        "name": "Маленький квартал",
        "territory_type": TerritoryType.DISTRICT,
        "description": "Тихий жилой район. Идеально для старта.",
        "influence_required": 25,
        "power_required": 20,
        "intellect_required": 15,
        "agility_required": 15,
        "reward_influence": 15,
        "reward_money": 200,
        "passive_income_money": 50,
        "passive_income_influence": 1,
        "display_order": 1,
    },
    {
        "name": "Портовый район",
        "territory_type": TerritoryType.DISTRICT,
        "description": "Грузовой порт. Контрабанда и чёрный рынок.",
        "influence_required": 40,
        "power_required": 25,
        "intellect_required": 20,
        "agility_required": 20,
        "reward_influence": 15,
        "reward_money": 300,
        "passive_income_money": 75,
        "passive_income_influence": 1,
        "display_order": 2,
    },
    {
        "name": "Торговый центр",
        "territory_type": TerritoryType.NEIGHBORHOOD,
        "description": "Крупный торговый район. Рэкет и защита.",
        "influence_required": 55,
        "power_required": 30,
        "intellect_required": 25,
        "agility_required": 20,
        "reward_influence": 20,
        "reward_money": 400,
        "passive_income_money": 100,
        "passive_income_influence": 1,
        "display_order": 3,
    },
    {
        "name": "Индустриальная зона",
        "territory_type": TerritoryType.NEIGHBORHOOD,
        "description": "Заводы и склады. Контрабандное производство.",
        "influence_required": 70,
        "power_required": 35,
        "intellect_required": 30,
        "agility_required": 25,
        "reward_influence": 20,
        "reward_money": 500,
        "passive_income_money": 125,
        "passive_income_influence": 1,
        "display_order": 4,
    },
    {
        "name": "Финансовый квартал",
        "territory_type": TerritoryType.BOROUGH,
        "description": "Банки и офисы. Отмывание денег и коррупция.",
        "influence_required": 85,
        "power_required": 30,
        "intellect_required": 40,
        "agility_required": 25,
        "reward_influence": 15,
        "reward_money": 600,
        "passive_income_money": 150,
        "passive_income_influence": 1,
        "display_order": 5,
    },
    {
        "name": "Развлекательный район",
        "territory_type": TerritoryType.BOROUGH,
        "description": "Казино, клубы, подпольные заведения.",
        "influence_required": 95,
        "power_required": 35,
        "intellect_required": 35,
        "agility_required": 30,
        "reward_influence": 10,
        "reward_money": 700,
        "passive_income_money": 175,
        "passive_income_influence": 1,
        "display_order": 6,
    },
    {
        "name": "Правительственный квартал",
        "territory_type": TerritoryType.BOROUGH,
        "description": "Мэрия, суды, полиция. Высший уровень влияния.",
        "influence_required": 100,
        "power_required": 40,
        "intellect_required": 45,
        "agility_required": 30,
        "reward_influence": 10,
        "reward_money": 800,
        "passive_income_money": 200,
        "passive_income_influence": 1,
        "display_order": 7,
    },
    {
        "name": "Центр города",
        "territory_type": TerritoryType.BOROUGH,
        "description": "Сердце империи. Контроль над всем городом.",
        "influence_required": 110,
        "power_required": 50,
        "intellect_required": 50,
        "agility_required": 40,
        "reward_influence": 10,
        "reward_money": 1000,
        "passive_income_money": 225,
        "passive_income_influence": 1,
        "display_order": 8,
    },
]


async def seed_territories():
    async with AsyncSession(bind=db_helper.engine) as session:
        # Check if territories already exist
        existing = await territory_crud.list(session)
        if existing:
            print(f"✅ {len(existing)} territories already exist, skipping")
            return

        for data in TERRITORIES:
            await territory_crud.create(session, data)

        await session.commit()
        print(f"✅ Created {len(TERRITORIES)} territories")


async def main():
    print("🌱 Seeding territories...")
    await seed_territories()
    await db_helper.engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
