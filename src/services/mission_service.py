from datetime import datetime, timedelta
from random import randint
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from services.base import BaseService
from crud.mission import mission_crud
from crud.other_crud import CRUDMissionEvent, User
from crud.user_mission import user_mission_crud

from models import (
    Mission,
    Character,
    UserMission,
    MissionStatus,
    MissionEventType,
)

# Инициализация CRUD
character_crud = CRUDCharacter(Character)
mission_crud = CRUDMission(Mission)
event_crud = CRUDMissionEvent(MissionEvent)

class MissionService(BaseService):
    """
    Сервис миссий:
    - запуск миссии
    - завершение миссии
    - расчёт характеристик
    - обработка событий
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, mission_crud)
        self.event_crud = mission_event_crud
        self.user_mission_crud = user_mission_crud

    # -------------------------
    # ХАРАКТЕРИСТИКИ
    # -------------------------

    async def calculate_character_effective_stats(self, character: Character):
        return {
            "power": character.power + sum(w.bonus_power for w in character.weapons),
            "intellect": character.intellect + sum(t.bonus_intellect for t in character.tools),
            "agility": character.agility + sum(t.bonus_agility for t in character.tools),
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

        total_power = 0
        total_intellect = 0
        total_agility = 0

        for c in characters:
            if c.is_busy:
                return False, f"Персонаж {c.id} уже занят"

            stats = await self.calculate_character_effective_stats(c)
            total_power += stats["power"]
            total_intellect += stats["intellect"]
            total_agility += stats["agility"]

        if total_power < mission.power_required:
            return False, "Недостаточно силы"
        if total_intellect < mission.intellect_required:
            return False, "Недостаточно интеллекта"
        if total_agility < mission.agility_required:
            return False, "Недостаточно ловкости"

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

        # блокируем персонажей
        for c in characters:
            c.is_busy = True

        user_mission = await self.user_mission_crud.create(
            self.session,
            {
                "user_id": user_id,
                "mission_id": mission_id,
                "status": MissionStatus.IN_PROGRESS,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow() + timedelta(seconds=mission.duration),
            },
        )

        await self.session.commit()

        return {
            "success": True,
            "message": "Миссия началась",
            "mission_id": user_mission.id,
            "ends_at": user_mission.completed_at,
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

        if datetime.utcnow() < user_mission.completed_at:
            return {"success": False, "message": "Миссия ещё выполняется"}

        mission: Mission = user_mission.mission

        # персонажи
        characters = user_mission.characters

        # события
        events = await self.event_crud.get_by_mission(self.session, mission.id)

        event_results = []
        success = True

        reward_money = mission.reward_money
        reward_influence = mission.reward_influence

        for event in events:
            roll = randint(1, 100)

            if roll > event.chance:
                continue

            if event.event_type == MissionEventType.POLICE_RAID:
                money_lost = min(roll * 10, reward_money)
                reward_money -= money_lost
                event_results.append(f"{event.description} | Потеря денег: {money_lost}")

            elif event.event_type == MissionEventType.COMPETITOR_ATTACK:
                reward_influence = max(0, reward_influence - 10)
                event_results.append(f"{event.description} | Потеря влияния")

            elif event.event_type == MissionEventType.RANDOM_LUCK:
                if randint(1, 100) > 20:
                    success = False
                    event_results.append(f"{event.description} | Провал")
                else:
                    event_results.append(f"{event.description} | Повезло")

        # освобождаем персонажей
        for c in characters:
            c.is_busy = False

        # обновляем статус
        user_mission.status = (
            MissionStatus.COMPLETED if success else MissionStatus.FAILED
        )

        # TODO: тут позже добавим начисление ресурсов пользователю

        await self.session.commit()

        return {
            "success": success,
            "events": event_results,
            "reward_money": reward_money if success else 0,
            "reward_influence": reward_influence if success else 0,
        }