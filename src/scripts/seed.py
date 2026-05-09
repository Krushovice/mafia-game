"""Seed script — заполняет БД тестовыми данными через ORM."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select

from core.database.db_helper import db_helper
from core.database.models import Mission, NPCBoss, ShopItem, Territory
from core.database.models.enums import (
    CharacterRole,
    CharacterTrait,
    MissionDifficulty,
    MissionStatType,
    ShopItemType,
    TerritoryType,
)


async def seed():
    async with db_helper._session_factory() as session:
        # 1. Shop Items
        existing = await session.execute(select(ShopItem))
        if existing.scalars().first():
            print("⏭️  Shop items already exist")
        else:
            shop_items = [
                # Бойцы
                ShopItem(
                    name="Боевик Вито",
                    description="Крепкий парень, хорош для силовых миссий",
                    item_type=ShopItemType.CHARACTER,
                    cost_money=500,
                    cost_influence=5,
                    role=CharacterRole.THUG,
                    trait=CharacterTrait.HOT,
                    base_power=25,
                    base_intellect=5,
                    base_agility=10,
                    base_loyalty=15,
                    display_order=1,
                ),
                ShopItem(
                    name="Хакер Нео",
                    description="Взламывает системы, незаменим для стелс-миссий",
                    item_type=ShopItemType.CHARACTER,
                    cost_money=600,
                    cost_influence=8,
                    role=CharacterRole.HACKER,
                    trait=CharacterTrait.QUIET,
                    base_power=5,
                    base_intellect=30,
                    base_agility=15,
                    base_loyalty=10,
                    display_order=2,
                ),
                ShopItem(
                    name="Переговорщик Сол",
                    description="Уговорит кого угодно, мастер дипломатии",
                    item_type=ShopItemType.CHARACTER,
                    cost_money=550,
                    cost_influence=6,
                    role=CharacterRole.NEGOTIATOR,
                    trait=CharacterTrait.GREEDY,
                    base_power=8,
                    base_intellect=20,
                    base_agility=25,
                    base_loyalty=12,
                    display_order=3,
                ),
                # Оружие
                ShopItem(
                    name="Пистолет",
                    description="Старый добрый 9мм, надёжный",
                    item_type=ShopItemType.WEAPON,
                    cost_money=200,
                    bonus_power=10,
                    display_order=10,
                ),
                ShopItem(
                    name="Дробовик",
                    description="Для серьёзных разборок, +15 к силе",
                    item_type=ShopItemType.WEAPON,
                    cost_money=400,
                    cost_influence=2,
                    bonus_power=15,
                    display_order=11,
                ),
                ShopItem(
                    name="Нож-бабочка",
                    description="Тихое оружие, не привлекает внимания",
                    item_type=ShopItemType.WEAPON,
                    cost_money=150,
                    bonus_power=5,
                    bonus_agility=5,
                    display_order=12,
                ),
                # Инструменты
                ShopItem(
                    name="Отмычки",
                    description="Набор профессионала для вскрытия замков",
                    item_type=ShopItemType.TOOL,
                    cost_money=180,
                    bonus_intellect=8,
                    bonus_agility=12,
                    display_order=20,
                ),
                ShopItem(
                    name="Планшет хакера",
                    description="Взлом камер и сигнализаций",
                    item_type=ShopItemType.TOOL,
                    cost_money=350,
                    cost_influence=3,
                    bonus_intellect=15,
                    bonus_agility=5,
                    display_order=21,
                ),
                ShopItem(
                    name="Фальшивые документы",
                    description="Помогут пройти проверку на КПП",
                    item_type=ShopItemType.TOOL,
                    cost_money=250,
                    cost_influence=2,
                    bonus_intellect=10,
                    bonus_agility=10,
                    display_order=22,
                ),
            ]
            session.add_all(shop_items)
            await session.commit()
            print(f"✅ Inserted {len(shop_items)} shop items")

        # 2. Missions
        existing_m = await session.execute(select(Mission))
        if existing_m.scalars().first():
            print("⏭️  Missions already exist")
        else:
            missions = [
                Mission(
                    name="Разборка в порту",
                    description="Конкуренты захватили склад в порту. Верни его силой!",
                    duration=120,
                    reward_money=300,
                    reward_influence=3,
                    wanted_increase=3,
                    difficulty=MissionDifficulty.EASY,
                    mission_stat_type=MissionStatType.FORCE,
                    slots=1,
                    power_required=15,
                ),
                Mission(
                    name="Кража документов",
                    description="Тихо проникнуть в офис конкурентов и забрать компромат",
                    duration=180,
                    reward_money=450,
                    reward_influence=5,
                    wanted_increase=2,
                    difficulty=MissionDifficulty.MEDIUM,
                    mission_stat_type=MissionStatType.STEALTH,
                    slots=2,
                    intellect_required=0,
                    agility_required=20,
                    tool_slots_required=1,
                ),
                Mission(
                    name="Переговоры с мэром",
                    description="Убеди мэра закрыть глаза на вашу деятельность",
                    duration=90,
                    reward_money=200,
                    reward_influence=8,
                    wanted_increase=1,
                    difficulty=MissionDifficulty.EASY,
                    mission_stat_type=MissionStatType.DIPLOMACY,
                    slots=1,
                    intellect_required=15,
                    agility_required=10,
                ),
                Mission(
                    name="Ограбление казино",
                    description="Серьёзная операция: взлом сейфа, отвлечение охраны, вынос налички",
                    duration=300,
                    reward_money=1200,
                    reward_influence=10,
                    wanted_increase=8,
                    difficulty=MissionDifficulty.HARD,
                    mission_stat_type=MissionStatType.STEALTH,
                    slots=3,
                    power_required=20,
                    intellect_required=25,
                    agility_required=20,
                    weapon_slots_required=1,
                    tool_slots_required=2,
                ),
                Mission(
                    name="⚡ Срочная доставка",
                    description="Нужно срочно доставить груз. Ограничено по времени!",
                    duration=60,
                    reward_money=600,
                    reward_influence=6,
                    wanted_increase=4,
                    difficulty=MissionDifficulty.MEDIUM,
                    mission_stat_type=MissionStatType.FORCE,
                    slots=2,
                    power_required=20,
                    agility_required=15,
                    reward_multiplier=1.5,
                ),
                Mission(
                    name="⚡ Ликвидация свидетеля",
                    description="Свидетель готов заговорить. Остановите его!",
                    duration=45,
                    reward_money=800,
                    reward_influence=8,
                    wanted_increase=6,
                    difficulty=MissionDifficulty.HARD,
                    mission_stat_type=MissionStatType.FORCE,
                    slots=1,
                    power_required=30,
                    agility_required=10,
                    weapon_slots_required=1,
                    reward_multiplier=2.0,
                ),
            ]
            session.add_all(missions)
            await session.commit()
            print(f"✅ Inserted {len(missions)} missions")

        # 3. NPC Bosses
        existing_b = await session.execute(select(NPCBoss))
        if existing_b.scalars().first():
            print("⏭️  NPC Bosses already exist")
        else:
            bosses = [
                NPCBoss(name="Дон Карлоне", color="#e74c3c", influence=15, power=20),
                NPCBoss(
                    name="Сеньор Маркетти", color="#3498db", influence=25, power=30
                ),
                NPCBoss(name="Барон Росси", color="#9b59b6", influence=40, power=45),
                NPCBoss(name="Граф Бианки", color="#f39c12", influence=55, power=60),
                NPCBoss(name="Герцог Верди", color="#2ecc71", influence=70, power=75),
                NPCBoss(name="Император Неро", color="#1abc9c", influence=85, power=90),
                NPCBoss(
                    name="Крёстный отец", color="#e67e22", influence=100, power=100
                ),
            ]
            session.add_all(bosses)
            await session.commit()
            print(f"✅ Inserted {len(bosses)} NPC bosses")

        # 4. Territories
        existing_t = await session.execute(select(Territory))
        if existing_t.scalars().first():
            print("⏭️  Territories already exist")
        else:
            territories = [
                Territory(
                    name="Квартал Красных Фонарей",
                    description="Шумный район с барами и клубами",
                    territory_type=TerritoryType.NEIGHBORHOOD,
                    influence_required=25,
                    power_required=20,
                    intellect_required=15,
                    agility_required=15,
                    reward_influence=15,
                    reward_money=200,
                    passive_income_money=50,
                    passive_income_influence=1,
                    display_order=1,
                    grid_x=0,
                    grid_y=0,
                    boss_id=1,  # Дон Карлоне
                ),
                Territory(
                    name="Промышленный район",
                    description="Заводы и склады, хороший доход",
                    territory_type=TerritoryType.DISTRICT,
                    influence_required=35,
                    power_required=30,
                    intellect_required=20,
                    agility_required=20,
                    reward_influence=20,
                    reward_money=300,
                    passive_income_money=75,
                    passive_income_influence=2,
                    display_order=2,
                    grid_x=1,
                    grid_y=0,
                    boss_id=2,  # Сеньор Маркетти
                ),
                Territory(
                    name="Финансовый квартал",
                    description="Банки и офисы, источник влияния",
                    territory_type=TerritoryType.BOROUGH,
                    influence_required=50,
                    power_required=40,
                    intellect_required=35,
                    agility_required=30,
                    reward_influence=30,
                    reward_money=500,
                    passive_income_money=100,
                    passive_income_influence=3,
                    display_order=3,
                    grid_x=2,
                    grid_y=0,
                    boss_id=3,  # Барон Росси
                ),
                Territory(
                    name="Портовый район",
                    description="Контрабанда и торговля",
                    territory_type=TerritoryType.DISTRICT,
                    influence_required=40,
                    power_required=35,
                    intellect_required=25,
                    agility_required=30,
                    reward_influence=25,
                    reward_money=400,
                    passive_income_money=90,
                    passive_income_influence=2,
                    display_order=4,
                    grid_x=0,
                    grid_y=1,
                    boss_id=4,  # Граф Бианки
                ),
                Territory(
                    name="Старый город",
                    description="Исторический центр, символ власти",
                    territory_type=TerritoryType.BOROUGH,
                    influence_required=70,
                    power_required=55,
                    intellect_required=45,
                    agility_required=40,
                    reward_influence=50,
                    reward_money=800,
                    passive_income_money=150,
                    passive_income_influence=5,
                    display_order=5,
                    grid_x=2,
                    grid_y=1,
                    boss_id=5,  # Герцог Верди
                ),
            ]
            session.add_all(territories)
            await session.commit()
            print(f"✅ Inserted {len(territories)} territories")

        print("\n🎉 Seed completed!")
        await session.close()


if __name__ == "__main__":
    asyncio.run(seed())
