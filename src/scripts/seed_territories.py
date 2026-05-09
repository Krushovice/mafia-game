"""Seed 7 территорий города Сан-Марчелло."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models.enums import TerritoryType
from crud.other_crud import territory_crud

# Пассивный доход за тик (10 мин) для всех 7 районов суммарно ~300 монет
# $$ = 15-20, $$$ = 35-45, $$$$ = 60-65
TERRITORIES = [
    {
        "id": 1,
        "name": "Уэст-Энд",
        "territory_type": TerritoryType.NEIGHBORHOOD,
        "description": "Рабочий квартал с дешёвыми забегаловками и ветхими складами. Стартовая база игрока.",
        "influence_required": 0,
        "influence_cost": 0,
        "power_required": 0,
        "intellect_required": 0,
        "agility_required": 0,
        "reward_influence": 0,
        "reward_money": 0,
        "passive_income_money": 15,
        "passive_income_influence": 1,
        "display_order": 1,
        "grid_x": 0,
        "grid_y": 1,
    },
    {
        "id": 2,
        "name": "Центральный Деловой",
        "territory_type": TerritoryType.DISTRICT,
        "description": "Небоскрёбы, банки и элитные рестораны. Самый прибыльный район.",
        "influence_required": 25,
        "influence_cost": 10,
        "power_required": 20,
        "intellect_required": 15,
        "agility_required": 15,
        "reward_influence": 15,
        "reward_money": 250,
        "passive_income_money": 60,
        "passive_income_influence": 2,
        "display_order": 2,
        "grid_x": 1,
        "grid_y": 1,
    },
    {
        "id": 3,
        "name": "Литл-Итали",
        "territory_type": TerritoryType.NEIGHBORHOOD,
        "description": "Рестораны, семейные лавки и старые традиции. Высокий доход от «крышевания».",
        "influence_required": 40,
        "influence_cost": 12,
        "power_required": 25,
        "intellect_required": 20,
        "agility_required": 20,
        "reward_influence": 18,
        "reward_money": 350,
        "passive_income_money": 40,
        "passive_income_influence": 2,
        "display_order": 3,
        "grid_x": 1,
        "grid_y": 0,
    },
    {
        "id": 4,
        "name": "Индустриальный",
        "territory_type": TerritoryType.DISTRICT,
        "description": "Заводы, склады и подпольные цеха. Контрабанда процветает.",
        "influence_required": 55,
        "influence_cost": 15,
        "power_required": 30,
        "intellect_required": 20,
        "agility_required": 25,
        "reward_influence": 20,
        "reward_money": 450,
        "passive_income_money": 20,
        "passive_income_influence": 1,
        "display_order": 4,
        "grid_x": 1,
        "grid_y": 2,
    },
    {
        "id": 5,
        "name": "Портовый Район",
        "territory_type": TerritoryType.BOROUGH,
        "description": "Доки, грузовые терминалы и контейнерные склады. Центр морской контрабанды.",
        "influence_required": 70,
        "influence_cost": 18,
        "power_required": 35,
        "intellect_required": 25,
        "agility_required": 25,
        "reward_influence": 22,
        "reward_money": 550,
        "passive_income_money": 40,
        "passive_income_influence": 2,
        "display_order": 5,
        "grid_x": 2,
        "grid_y": 2,
    },
    {
        "id": 6,
        "name": "Риверсайд",
        "territory_type": TerritoryType.NEIGHBORHOOD,
        "description": "Стильный прибрежный район с казино и ночными клубами.",
        "influence_required": 85,
        "influence_cost": 20,
        "power_required": 35,
        "intellect_required": 30,
        "agility_required": 30,
        "reward_influence": 25,
        "reward_money": 650,
        "passive_income_money": 45,
        "passive_income_influence": 2,
        "display_order": 6,
        "grid_x": 2,
        "grid_y": 1,
    },
    {
        "id": 7,
        "name": "Холмы",
        "territory_type": TerritoryType.DISTRICT,
        "description": "Особняки, закрытые клубы и элита города. Самый престижный квартал.",
        "influence_required": 95,
        "influence_cost": 25,
        "power_required": 40,
        "intellect_required": 35,
        "agility_required": 35,
        "reward_influence": 30,
        "reward_money": 800,
        "passive_income_money": 65,
        "passive_income_influence": 3,
        "display_order": 7,
        "grid_x": 2,
        "grid_y": 0,
    },
]


async def seed_territories():
    """Идемпотентный upsert: обновляет существующие записи по id, создаёт недостающие."""
    async with AsyncSession(bind=db_helper.engine) as session:
        created = 0
        updated = 0
        for data in TERRITORIES:
            existing = await territory_crud.get(session, data["id"])
            if existing:
                await territory_crud.update(session, data["id"], data, commit=False)
                updated += 1
            else:
                await territory_crud.create(session, data, commit=False)
                created += 1

        await session.commit()
        print(f"✅ Территории: создано {created}, обновлено {updated}")


async def main():
    print("🌱 Заполняем территории...")
    await seed_territories()
    await db_helper.engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
