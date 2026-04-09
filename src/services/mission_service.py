from datetime import datetime, timedelta, timezone
from random import randint
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Character, Mission, UserMission
from core.database.models.enums import MissionEventType, MissionStatType, MissionStatus
from crud.other_crud import (
    character_crud,
    mission_character_crud,
    mission_crud,
    mission_event_crud,
    user_mission_crud,
    user_resource_crud,
)

from .base_service import BaseService


class MissionService(BaseService):
    """Service for mission lifecycle: start, complete, event processing."""

    # Коэффициенты расчёта наград от главного стата
    REWARD_MONEY_PER_STAT = 15
    REWARD_INFLUENCE_PER_STAT = 3
    WANTED_PER_STAT = 10

    def __init__(self, session: AsyncSession):
        super().__init__(session, mission_crud)
        self.character_crud = character_crud
        self.event_crud = mission_event_crud
        self.user_mission_crud = user_mission_crud
        self.mission_character_crud = mission_character_crud

    # -------------------------
    # ХАРАКТЕРИСТИКИ
    # -------------------------

    async def calculate_character_effective_stats(self, character: Character):
        # load equipment explicitly to avoid lazy-loading outside greenlet
        from core.database.models import Tool, Weapon

        weapons = (
            (
                await self.session.execute(
                    select(Weapon).where(Weapon.owner_id == character.id)
                )
            )
            .scalars()
            .all()
        )
        tools = (
            (
                await self.session.execute(
                    select(Tool).where(Tool.owner_id == character.id)
                )
            )
            .scalars()
            .all()
        )

        return {
            "power": character.power + sum(w.bonus_power for w in weapons),
            "intellect": character.intellect + sum(t.bonus_intellect for t in tools),
            "agility": character.agility + sum(t.bonus_agility for t in tools),
            "weapons_count": len(weapons),
            "tools_count": len(tools),
        }

    # -------------------------
    # РАСЧЁТ НАГРАД
    # -------------------------

    def calculate_mission_rewards(
        self, mission: Mission, characters: List[Character]
    ) -> dict:
        """Рассчитать награды на основе главного стата миссии.

        Главный стат определяется mission_stat_type:
          - force → total_power
          - stealth → total_agility
          - diplomacy → total_intellect

        Формула:
          reward_money = main_stat_value * 15 * reward_multiplier
          reward_influence = (main_stat_value // 3) * reward_multiplier
          wanted_increase = max(1, main_stat_value // 10)
        """
        total_power = 0
        total_intellect = 0
        total_agility = 0

        for c in characters:
            stats = {
                "power": c.power,
                "intellect": c.intellect,
                "agility": c.agility,
            }
            # Добавляем бонусы от экипировки (упрощённо, без запроса к БД)
            total_power += stats["power"]
            total_intellect += stats["intellect"]
            total_agility += stats["agility"]

        # Определяем главный стат
        main_stat_map = {
            MissionStatType.FORCE: total_power,
            MissionStatType.STEALTH: total_agility,
            MissionStatType.DIPLOMACY: total_intellect,
        }
        main_stat_value = main_stat_map.get(mission.mission_stat_type, total_power)

        reward_money = int(
            main_stat_value * self.REWARD_MONEY_PER_STAT * mission.reward_multiplier
        )
        reward_influence = max(
            1,
            int(
                main_stat_value
                // self.REWARD_INFLUENCE_PER_STAT
                * mission.reward_multiplier
            ),
        )
        wanted_increase = max(1, main_stat_value // self.WANTED_PER_STAT)

        return {
            "reward_money": reward_money,
            "reward_influence": reward_influence,
            "wanted_increase": wanted_increase,
            "main_stat_value": main_stat_value,
        }

    # -------------------------
    # ПРОВЕРКА МИССИИ
    # -------------------------

    async def is_mission_possible(
        self,
        mission: Mission,
        characters: List[Character],
    ):
        if len(characters) > mission.slots:
            return False, "Слишком много персонажей"

        if len(characters) == 0:
            return False, "Нужен хотя бы один персонаж"

        total_power = 0
        total_intellect = 0
        total_agility = 0
        total_weapons = 0
        total_tools = 0

        for c in characters:
            if c.is_busy:
                return False, f"Персонаж {c.name} уже занят"

            stats = await self.calculate_character_effective_stats(c)
            total_power += stats["power"]
            total_intellect += stats["intellect"]
            total_agility += stats["agility"]
            total_weapons += stats["weapons_count"]
            total_tools += stats["tools_count"]

        if total_power < mission.power_required:
            return False, f"Недостаточно силы ({total_power}/{mission.power_required})"
        if total_intellect < mission.intellect_required:
            return (
                False,
                f"Недостаточно интеллекта ({total_intellect}/{mission.intellect_required})",
            )
        if total_agility < mission.agility_required:
            return (
                False,
                f"Недостаточно ловкости ({total_agility}/{mission.agility_required})",
            )

        # Проверка экипировки
        if total_weapons < mission.weapon_slots_required:
            return (
                False,
                f"Нужно {mission.weapon_slots_required} оружия, есть {total_weapons}",
            )
        if total_tools < mission.tool_slots_required:
            return (
                False,
                f"Нужно {mission.tool_slots_required} инструментов, есть {total_tools}",
            )

        return True, "OK"

    # -------------------------
    # СТАРТ МИССИИ
    # -------------------------

    async def start_mission(
        self,
        user_id: int,
        mission_id: int,
        characters: List[Character],
    ):
        mission = await self.get(mission_id)
        if not mission:
            return {"success": False, "message": "Миссия не найдена"}

        possible, msg = await self.is_mission_possible(mission, characters)
        if not possible:
            return {"success": False, "message": msg}

        # Рассчитываем награды заранее
        rewards = self.calculate_mission_rewards(mission, characters)

        # Выполняем изменения в рамках транзакции (start only if no active transaction)
        if self.session.in_transaction():
            # блокируем персонажей
            for c in characters:
                c.is_busy = True

            # Создаём запись UserMission (отложенно, без отдельного коммита)
            user_mission = await self.user_mission_crud.create(
                self.session,
                {
                    "user_id": user_id,
                    "mission_id": mission_id,
                    "status": MissionStatus.IN_PROGRESS,
                    "started_at": datetime.now(timezone.utc),
                    "ends_at": datetime.now(timezone.utc) + timedelta(seconds=mission.duration),
                    "success_chance": 100,
                    # Сохраняем рассчитанные награды
                    "reward_money": rewards["reward_money"],
                    "reward_influence": rewards["reward_influence"],
                    "wanted_increase": rewards["wanted_increase"],
                },
                commit=False,
            )

            # flush to get generated ids
            await self.session.flush()

            # Связываем персонажей с миссией
            for idx, c in enumerate(characters):
                await self.mission_character_crud.create_link(
                    self.session, user_mission.id, c.id, idx, commit=False
                )
        else:
            async with self.session.begin():
                # блокируем персонажей
                for c in characters:
                    c.is_busy = True

                # Создаём запись UserMission (отложенно, без отдельного коммита)
                user_mission = await self.user_mission_crud.create(
                    self.session,
                    {
                        "user_id": user_id,
                        "mission_id": mission_id,
                        "status": MissionStatus.IN_PROGRESS,
                        "started_at": datetime.now(timezone.utc),
                        "ends_at": datetime.now(timezone.utc)
                        + timedelta(seconds=mission.duration),
                        "success_chance": 100,
                        # Сохраняем рассчитанные награды
                        "reward_money": rewards["reward_money"],
                        "reward_influence": rewards["reward_influence"],
                        "wanted_increase": rewards["wanted_increase"],
                    },
                    commit=False,
                )

                # flush to get generated ids
                await self.session.flush()

                # Связываем персонажей с миссией
                for idx, c in enumerate(characters):
                    await self.mission_character_crud.create_link(
                        self.session, user_mission.id, c.id, idx, commit=False
                    )

        return {
            "success": True,
            "message": "Миссия началась",
            "mission_id": user_mission.id,
            "ends_at": user_mission.ends_at,
            "rewards": rewards,
        }

    # -------------------------
    # ЗАВЕРШЕНИЕ МИССИИ
    # -------------------------

    async def complete_mission(self, user_mission_id: int):
        user_mission: UserMission = await self.user_mission_crud.get(
            self.session, user_mission_id
        )

        if not user_mission:
            return {"success": False, "message": "Миссия не найдена"}

        if user_mission.status != MissionStatus.IN_PROGRESS:
            return {"success": False, "message": "Миссия уже завершена"}

        if datetime.now(timezone.utc) < user_mission.ends_at:
            return {"success": False, "message": "Миссия ещё выполняется"}

        mission: Mission = user_mission.mission

        # персонажи: загружаем привязки и связанные персонажи явным запросом
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from core.database.models import MissionCharacter

        mchars = (
            (
                await self.session.execute(
                    select(MissionCharacter)
                    .options(selectinload(MissionCharacter.character))
                    .where(MissionCharacter.user_mission_id == user_mission_id)
                )
            )
            .scalars()
            .all()
        )
        characters = [mc.character for mc in mchars]

        # события
        events = await self.event_crud.list_by_mission(self.session, mission.id)

        event_results = []
        success = True

        reward_money = user_mission.reward_money or 0
        reward_influence = user_mission.reward_influence or 0
        wanted_increase = user_mission.wanted_increase or 1

        for event in events:
            roll = randint(1, 100)

            if roll > event.chance:
                continue

            if event.event_type == MissionEventType.POLICE_RAID:
                money_lost = min(roll * 10, reward_money)
                reward_money -= money_lost
                event_results.append(
                    f"{event.description} | Потеря денег: {money_lost}"
                )

            elif event.event_type == MissionEventType.COMPETITOR_ATTACK:
                reward_influence = max(0, reward_influence - 10)
                event_results.append(f"{event.description} | Потеря влияния")

            elif event.event_type == MissionEventType.RANDOM_LUCK:
                if randint(1, 100) > 20:
                    success = False
                    event_results.append(f"{event.description} | Провал")
                else:
                    event_results.append(f"{event.description} | Повезло")

        # Начисляем награды и обновляем статус в транзакции
        if self.session.in_transaction():
            for c in characters:
                c.is_busy = False

            user_mission.status = (
                MissionStatus.COMPLETED if success else MissionStatus.FAILED
            )
            user_mission.result = {
                "success": success,
                "events": event_results,
                "reward_money": reward_money if success else 0,
                "reward_influence": reward_influence if success else 0,
                "wanted_increase": wanted_increase,
            }

            # Начисляем ресурсы пользователю
            if success:
                resources = await user_resource_crud.get_by_user(
                    self.session, user_mission.user_id
                )
                if resources:
                    resources.money += reward_money if reward_money else 0
                    resources.influence += reward_influence if reward_influence else 0
                    resources.wanted_level += wanted_increase
                else:
                    await user_resource_crud.create(
                        self.session,
                        {
                            "user_id": user_mission.user_id,
                            "money": reward_money if reward_money else 0,
                            "influence": (reward_influence if reward_influence else 0),
                            "wanted_level": wanted_increase,
                        },
                        commit=False,
                    )
        else:
            async with self.session.begin():
                for c in characters:
                    c.is_busy = False

                user_mission.status = (
                    MissionStatus.COMPLETED if success else MissionStatus.FAILED
                )
                user_mission.result = {
                    "success": success,
                    "events": event_results,
                    "reward_money": reward_money if success else 0,
                    "reward_influence": reward_influence if success else 0,
                    "wanted_increase": wanted_increase,
                }

                # Начисляем ресурсы пользователю
                if success:

                    resources = await user_resource_crud.get_by_user(
                        self.session, user_mission.user_id
                    )
                    if resources:
                        resources.money += reward_money if reward_money else 0
                        resources.influence += (
                            reward_influence if reward_influence else 0
                        )
                        resources.wanted_level += wanted_increase
                    else:
                        await user_resource_crud.create(
                            self.session,
                            {
                                "user_id": user_mission.user_id,
                                "money": reward_money if reward_money else 0,
                                "influence": (
                                    reward_influence if reward_influence else 0
                                ),
                                "wanted_level": wanted_increase,
                            },
                            commit=False,
                        )

        return {
            "success": success,
            "events": event_results,
            "reward_money": reward_money if success else 0,
            "reward_influence": reward_influence if success else 0,
            "wanted_increase": wanted_increase,
        }
