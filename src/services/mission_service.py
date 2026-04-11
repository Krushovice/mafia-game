from datetime import datetime, timedelta, timezone
from random import randint
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Character, Mission, UserMission
from core.database.models.enums import MissionStatType, MissionStatus
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
    REWARD_MONEY_PER_STAT = 10  # ~2850 coins за заход (13 миссий mix)
    REWARD_INFLUENCE_PER_STAT = 3

    # Wanted increase зависит от сложности миссии
    WANTED_BY_DIFFICULTY = {
        "easy": 6,  # ~13 миссий до wanted=80
        "medium": 8,  # ~10 миссий до wanted=80
        "hard": 12,  # ~6-7 миссий до wanted=80
    }

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
            "intellect": character.intellect
            + sum(t.bonus_intellect for t in tools),
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
          reward_money = main_stat_value * 10 * reward_multiplier
          reward_influence = (main_stat_value // 3) * reward_multiplier
          wanted_increase = depends on difficulty (easy=6, medium=8, hard=12)
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
        main_stat_value = main_stat_map.get(
            mission.mission_stat_type, total_power
        )

        reward_money = int(
            main_stat_value
            * self.REWARD_MONEY_PER_STAT
            * mission.reward_multiplier
        )
        reward_influence = max(
            1,
            int(
                main_stat_value
                // self.REWARD_INFLUENCE_PER_STAT
                * mission.reward_multiplier
            ),
        )
        wanted_increase = self.WANTED_BY_DIFFICULTY.get(
            mission.difficulty.value, 6
        )

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
            return (
                False,
                f"Недостаточно силы ({total_power}/{mission.power_required})",
            )
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
        # Проверка уровня розыска — при wanted > 80 миссии заблокированы
        from crud.other_crud import user_resource_crud

        resources = await user_resource_crud.get_by_user(self.session, user_id)
        if resources and resources.wanted_level > 80:
            return {
                "success": False,
                "message": f"Уровень розыска слишком высок ({resources.wanted_level}). Подождите снижения.",
            }

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
                    self.session,
                    user_mission.id,
                    c.id,
                    idx,
                    commit=False,
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
                        self.session,
                        user_mission.id,
                        c.id,
                        idx,
                        commit=False,
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
        """Завершить миссию. Если сработало событие (10%) — приостановить и ждать выбора."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from core.database.models import MissionCharacter

        user_mission: UserMission = await self.user_mission_crud.get(
            self.session, user_mission_id
        )

        if not user_mission:
            return {"success": False, "message": "Миссия не найдена"}

        if user_mission.status != MissionStatus.IN_PROGRESS:
            return {
                "success": False,
                "message": "Миссия уже завершена",
            }

        if datetime.now(timezone.utc) < user_mission.ends_at:
            return {
                "success": False,
                "message": "Миссия ещё выполняется",
            }

        mission: Mission = user_mission.mission

        # Загружаем персонажей
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

        # Проверяем случайное событие (10% шанс)
        events = await self.event_crud.list_by_mission(self.session, mission.id)
        triggered_event = None

        for event in events:
            roll = randint(1, 100)
            if roll <= event.chance:
                triggered_event = event
                break

        if triggered_event:
            # Событие сработало — создаём запись лога и приостанавливаем миссию
            return await self._trigger_event(
                user_mission, triggered_event, characters
            )

        # Нет событий — завершаем сразу
        return await self._finalize_mission(
            user_mission, characters, success=True, event_results=[]
        )

    # -------------------------
    # СОБЫТИЯ
    # -------------------------

    async def _trigger_event(
        self,
        user_mission: UserMission,
        event,
        characters: List[Character],
    ):
        """Создать активное событие и приостановить миссию."""
        from crud.other_crud import (
            mission_event_choice_crud,
            user_mission_event_log_crud,
        )

        # Получаем варианты выбора для этого события
        choices = await mission_event_choice_crud.list_by_event(
            self.session, event.id
        )

        if self.session.in_transaction():
            user_mission.status = MissionStatus.WAITING_EVENT
        else:
            async with self.session.begin():
                user_mission.status = MissionStatus.WAITING_EVENT

        # Создаём запись лога
        event_log = await user_mission_event_log_crud.create(
            self.session,
            {
                "user_mission_id": user_mission.id,
                "resolved": False,
                "success": None,
                "result_description": None,
            },
            commit=False,
        )
        await self.session.flush()

        return {
            "success": True,
            "event_triggered": True,
            "event_log_id": event_log.id,
            "event_type": event.event_type.value,
            "event_description": event.description,
            "choices": [
                {
                    "id": c.id,
                    "choice_type": c.choice_type.value,
                    "label": c.label,
                    "description": c.description,
                    "money_cost": c.money_cost,
                    "influence_required": c.influence_required,
                    "power_required": c.power_required,
                    "success_chance_base": c.success_chance_base,
                }
                for c in choices
            ],
        }

    async def get_active_event(self, user_mission_id: int, user_id: int):
        """Получить текущее активное событие миссии."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from core.database.models import UserMission
        from crud.other_crud import (
            mission_event_choice_crud,
            user_mission_event_log_crud,
        )

        user_mission = (
            await self.session.execute(
                select(UserMission)
                .options(selectinload(UserMission.mission))
                .where(
                    UserMission.id == user_mission_id,
                    UserMission.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if not user_mission:
            return None

        if user_mission.status != MissionStatus.WAITING_EVENT:
            return None

        event_log = await user_mission_event_log_crud.get_active(
            self.session, user_mission_id
        )
        if not event_log:
            return None

        # Определяем тип события из миссии
        events = await self.event_crud.list_by_mission(
            self.session, user_mission.mission_id
        )
        if not events:
            return None

        event = events[0]  # берём первое событие
        choices = await mission_event_choice_crud.list_by_event(
            self.session, event.id
        )

        return {
            "event_log_id": event_log.id,
            "event_type": event.event_type.value,
            "event_description": event.description,
            "choices": [
                {
                    "id": c.id,
                    "event_id": c.event_id,
                    "choice_type": c.choice_type,
                    "label": c.label,
                    "description": c.description,
                    "money_cost": c.money_cost,
                    "influence_required": c.influence_required,
                    "power_required": c.power_required,
                    "success_chance_base": c.success_chance_base,
                }
                for c in choices
            ],
        }

    async def respond_event(
        self, user_mission_id: int, user_id: int, choice_type
    ):
        """Обработать выбор игрока по событию."""

        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from core.database.models import MissionCharacter, UserMission
        from crud.other_crud import (
            mission_event_choice_crud,
            user_mission_event_log_crud,
        )

        user_mission = (
            await self.session.execute(
                select(UserMission)
                .options(selectinload(UserMission.mission))
                .where(
                    UserMission.id == user_mission_id,
                    UserMission.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if not user_mission:
            return {"success": False, "message": "Миссия не найдена"}

        if user_mission.status != MissionStatus.WAITING_EVENT:
            return {
                "success": False,
                "message": "Нет активного события",
            }

        event_log = await user_mission_event_log_crud.get_active(
            self.session, user_mission_id
        )
        if not event_log:
            return {
                "success": False,
                "message": "Нет активного события",
            }

        # Загружаем персонажей
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

        # Находим событие и выбор
        mission = user_mission.mission
        events = await self.event_crud.list_by_mission(self.session, mission.id)
        if not events:
            return {"success": False, "message": "Событие не найдено"}

        event = events[0]
        choices = await mission_event_choice_crud.list_by_event(
            self.session, event.id
        )
        choice = next(
            (c for c in choices if c.choice_type == choice_type), None
        )

        if not choice:
            return {"success": False, "message": "Неверный тип выбора"}

        # Рассчитываем исход
        success, description = await self._resolve_choice(
            choice, user_mission, characters
        )

        # Обновляем лог
        if self.session.in_transaction():
            event_log.chosen_type = choice_type
            event_log.resolved = True
            event_log.success = success
            event_log.result_description = description
        else:
            async with self.session.begin():
                event_log.chosen_type = choice_type
                event_log.resolved = True
                event_log.success = success
                event_log.result_description = description

        # Завершаем миссию
        event_results = [f"{event.description} → {description}"]
        return await self._finalize_mission(
            user_mission,
            characters,
            success=success,
            event_results=event_results,
        )

    async def _resolve_choice(
        self,
        choice,
        user_mission: UserMission,
        characters: List[Character],
    ):
        """Рассчитать результат выбора игрока. Возвращает (success, description)."""
        from crud.other_crud import user_resource_crud

        resources = await user_resource_crud.get_by_user(
            self.session, user_mission.user_id
        )

        if choice.choice_type.value == "do_nothing":
            # Бездействие → провал
            if user_mission.mission_id:  # any mission
                # Для random_luck — это просто принятие удачи
                return True, "Удача принята"
            return False, "Бездействие. Миссия провалена."

        if choice.choice_type.value == "payoff":
            # Откуп — проверяем деньги
            if resources and resources.money >= choice.money_cost:
                resources.money -= choice.money_cost
                return True, f"Откупился. -{choice.money_cost} монет"
            return False, "Недостаточно денег для откупа."

        if choice.choice_type.value == "talk":
            # Заговорить зубы — базовый шанс * (1 + influence / 100)
            # При influence=100 → шанс удваивается (20% → 40%)
            if resources and resources.influence >= choice.influence_required:
                chance = int(
                    choice.success_chance_base * (1 + resources.influence / 100)
                )
                chance = min(chance, 95)
                if randint(1, 100) <= chance:
                    return (
                        True,
                        f"Удалось заговорить зубы! (шанс: {chance}%)",
                    )
                return (
                    False,
                    f"Не удалось заговорить зубы. (шанс: {chance}%)",
                )
            return False, "Недостаточно влияния."

        if choice.choice_type.value == "fight":
            # Бой — зависит от оружия и силы
            from sqlalchemy import select

            from core.database.models import Weapon

            total_power = sum(c.power for c in characters)
            weapon_count = 0
            for c in characters:
                weapons = (
                    (
                        await self.session.execute(
                            select(Weapon).where(Weapon.owner_id == c.id)
                        )
                    )
                    .scalars()
                    .all()
                )
                weapon_count += len(weapons)
                total_power += sum(w.bonus_power for w in weapons)

            if weapon_count < 1:
                return False, "Нет оружия для боя!"

            # Базовый 50% + бонус за избыток силы + бонус за оружие
            power_diff = total_power - choice.power_required
            chance = 50 + power_diff * 2 + weapon_count * 3
            chance = max(10, min(chance, 95))

            if randint(1, 100) <= chance:
                return True, f"Отбили атаку! (шанс: {chance}%)"
            return False, f"Не удалось отбить атаку. (шанс: {chance}%)"

        return False, "Неизвестный тип выбора."

    async def _finalize_mission(
        self,
        user_mission: UserMission,
        characters: List[Character],
        success: bool,
        event_results: list,
    ):
        """Завершить миссию: освободить персонажей, начислить награды."""
        reward_money = user_mission.reward_money or 0
        reward_influence = user_mission.reward_influence or 0
        wanted_increase = user_mission.wanted_increase or 1

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
                            "money": (reward_money if reward_money else 0),
                            "influence": (
                                reward_influence if reward_influence else 0
                            ),
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
                    "reward_influence": (reward_influence if success else 0),
                    "wanted_increase": wanted_increase,
                }

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
                                "money": (reward_money if reward_money else 0),
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
            "territory_captured": False,
        }
