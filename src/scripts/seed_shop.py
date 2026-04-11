"""Seed default shop items."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models.enums import (
    CharacterRole,
    CharacterTrait,
    ShopItemType,
)
from crud.other_crud import shop_item_crud

SHOP_ITEMS = [
    # Персонажи
    {
        "name": "Боевик",
        "description": "Крепкий парень для силовых операций.",
        "item_type": ShopItemType.CHARACTER,
        "cost_money": 500,
        "cost_influence": 0,
        "role": CharacterRole.THUG,
        "trait": CharacterTrait.HOT,
        "base_power": 20,
        "base_intellect": 5,
        "base_agility": 10,
        "base_loyalty": 10,
        "display_order": 1,
    },
    {
        "name": "Хакер",
        "description": "Мастер взлома и цифровых операций.",
        "item_type": ShopItemType.CHARACTER,
        "cost_money": 800,
        "cost_influence": 0,
        "role": CharacterRole.HACKER,
        "trait": CharacterTrait.QUIET,
        "base_power": 5,
        "base_intellect": 25,
        "base_agility": 10,
        "base_loyalty": 8,
        "display_order": 2,
    },
    {
        "name": "Переговорщик",
        "description": "Умеет договариваться с кем угодно.",
        "item_type": ShopItemType.CHARACTER,
        "cost_money": 600,
        "cost_influence": 0,
        "role": CharacterRole.NEGOTIATOR,
        "trait": CharacterTrait.QUIET,
        "base_power": 8,
        "base_intellect": 20,
        "base_agility": 15,
        "base_loyalty": 12,
        "display_order": 3,
    },
    # Оружие
    {
        "name": "Нож",
        "description": "Тихий и надёжный.",
        "item_type": ShopItemType.WEAPON,
        "cost_money": 150,
        "cost_influence": 0,
        "bonus_power": 3,
        "display_order": 10,
    },
    {
        "name": "Пистолет",
        "description": "Классика уличных разборок.",
        "item_type": ShopItemType.WEAPON,
        "cost_money": 400,
        "cost_influence": 0,
        "bonus_power": 8,
        "display_order": 11,
    },
    # Инструменты
    {
        "name": "Отмычки",
        "description": "Для тихого проникновения.",
        "item_type": ShopItemType.TOOL,
        "cost_money": 200,
        "cost_influence": 0,
        "bonus_intellect": 2,
        "bonus_agility": 3,
        "display_order": 20,
    },
    {
        "name": "Шифратор",
        "description": "Помогает взламывать цифровые замки.",
        "item_type": ShopItemType.TOOL,
        "cost_money": 350,
        "cost_influence": 0,
        "bonus_intellect": 5,
        "bonus_agility": 1,
        "display_order": 21,
    },
]


async def seed_shop_items():
    async with AsyncSession(bind=db_helper.engine) as session:
        existing = await shop_item_crud.list(session)
        if existing:
            print(f"✅ {len(existing)} shop items already exist, skipping")
            return

        for data in SHOP_ITEMS:
            await shop_item_crud.create(session, data)

        await session.commit()
        print(f"✅ Created {len(SHOP_ITEMS)} shop items")


async def main():
    print("🌱 Seeding shop items...")
    await seed_shop_items()
    await db_helper.engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
