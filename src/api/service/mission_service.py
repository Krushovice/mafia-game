from random import randint
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession


from core.database.models import Character, Mission, MissionEvent
from core.database.models.enums import MissionEventType
from core.crud.other_crud import CRUDCharacter, CRUDMission, CRUDMissionEvent

# Инициализация CRUD
character_crud = CRUDCharacter(Character)
mission_crud = CRUDMission(Mission)
event_crud = CRUDMissionEvent(MissionEvent)


class MissionService:
    """
    Сервисный слой миссий.
    - Проверка требований миссии
    - Распределение персонажей по слотам
    - События миссии и последствия
    """

    @staticmethod
    async def calculate_character_effective_stats(character: Character):
        """Суммирует базовые характеристики персонажа + бонусы оружия/инструментов"""
        power = character.power + sum(w.bonus_power for w in character.weapons)
        intellect = character.intellect + sum(t.bonus_intellect for t in character.tools)
        agility = character.agility + sum(t.bonus_agility for t in character.tools)
        return {"power": power, "intellect": intellect, "agility": agility}

    @staticmethod
    async def is_mission_possible(mission: Mission, characters: List[Character]):
        """Проверяет, хватает ли персонажей и соответствуют ли характеристики"""
        if len(characters) > mission.slots:
            return False, "Слишком много персонажей для слотов миссии"

        total_power = sum(await MissionService.calculate_character_effective_stats(c)["power"] for c in characters)
        total_intellect = sum(await MissionService.calculate_character_effective_stats(c)["intellect"] for c in characters)
        total_agility = sum(await MissionService.calculate_character_effective_stats(c)["agility"] for c in characters)

        if total_power < mission.power_required:
            return False, "Недостаточно силы"
        if total_intellect < mission.intellect_required:
            return False, "Недостаточно интеллекта"
        if total_agility < mission.agility_required:
            return False, "Недостаточно ловкости"

        return True, "Миссия возможна"

    @staticmethod
    async def run_mission(session: AsyncSession, mission_id: int, characters: List[Character]):
        """
        Основная логика выполнения миссии:
        - Проверка возможности
        - Генерация событий
        - Расчёт успеха
        - Обновление ресурсов игрока
        """
        mission = await mission_crud.get(session, mission_id)
        if not mission:
            return {"success": False, "message": "Миссия не найдена"}

        possible, msg = await MissionService.is_mission_possible(mission, characters)
        if not possible:
            return {"success": False, "message": msg}

        # События миссии
        events = await event_crud.list_by_mission(session, mission.id)
        event_results = []
        success = True

        for event in events:
            roll = randint(1, 100)
            if roll <= event.chance:
                # Событие произошло
                if event.event_type == MissionEventType.BRIBE:
                    # Потеря денег за возможность избежать влияния
                    money_lost = min(roll * 10, mission.reward_money)
                    mission.reward_money -= money_lost
                    event_results.append(f"Событие: {event.description} | Потрачено денег: {money_lost}")
                elif event.event_type == MissionEventType.LOSE_INFLUENCE:
                    mission.reward_influence = max(0, mission.reward_influence - 10)
                    event_results.append(f"Событие: {event.description} | Потеря влияния: 10")
                elif event.event_type == MissionEventType.CHANCE_ESCAPE:
                    chance_roll = randint(1, 100)
                    if chance_roll <= 20:
                        event_results.append(f"Событие: {event.description} | Удалось уйти сухим")
                    else:
                        success = False
                        event_results.append(f"Событие: {event.description} | Не удалось уйти")

        # Если нет критических событий, миссия успешна
        if success:
            for c in characters:
                c.is_busy = False
            await session.commit()
            return {
                "success": True,
                "message": "Миссия выполнена успешно",
                "events": event_results,
                "reward_money": mission.reward_money,
                "reward_influence": mission.reward_influence
            }
        else:
            return {
                "success": False,
                "message": "Миссия провалена",
                "events": event_results
            }