"""Influence decay and return mission service."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import User, UserMission
from core.database.models.enums import MissionStatus
from crud.other_crud import user_mission_crud, user_resource_crud


class InfluenceDecayService:
    """Decay влияния за время отсутствия игрока."""

    # Grace period — первые 4 часа без decay
    GRACE_HOURS = 4
    # Максимальный decay за одно отсутствие
    MAX_DECAY = 5
    # Порог появления возвратной миссии
    RETURN_MISSION_HOURS = 20

    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_decay(self, user: User) -> int:
        """Рассчитать потерю влияния с момента последнего входа."""
        last_login = user.created_at  # TODO: добавить last_login_at в User
        now = datetime.utcnow()
        hours_away = (now - last_login).total_seconds() / 3600

        if hours_away <= self.GRACE_HOURS:
            return 0

        decay = min(
            int(hours_away - self.GRACE_HOURS),
            self.MAX_DECAY,
        )
        return decay

    async def apply_decay(self, user_id: int) -> dict:
        """Применить decay влияния. Возвращает {decay, needs_return_mission}."""
        from crud.other_crud import user_crud

        user = await user_crud.get(self.session, user_id)
        if not user:
            return {"decay": 0, "needs_return_mission": False}

        decay = await self.calculate_decay(user)
        if decay <= 0:
            return {"decay": 0, "needs_return_mission": False}

        resources = await user_resource_crud.get_by_user(self.session, user_id)
        if not resources:
            return {"decay": 0, "needs_return_mission": False}

        old_influence = resources.influence
        resources.influence = max(0, resources.influence - decay)
        actual_decay = old_influence - resources.influence

        needs_return_mission = actual_decay >= 4
        hours_away = (datetime.utcnow() - user.created_at).total_seconds() / 3600
        if hours_away >= self.RETURN_MISSION_HOURS:
            needs_return_mission = True

        return {
            "decay": actual_decay,
            "needs_return_mission": needs_return_mission,
            "influence_before": old_influence,
            "influence_after": resources.influence,
        }

    def is_newbie(self, user: User) -> bool:
        """Проверка — новичок ли пользователь."""
        if (datetime.utcnow() - user.created_at).days < 7:
            return True
        return False

    async def get_or_create_return_mission(
        self, user_id: int, is_newbie: bool
    ) -> dict | None:
        """Создать или вернуть существующую возвратную миссию."""
        # Проверяем есть ли уже активная возвратная миссия
        result = await self.session.execute(
            select(UserMission).where(
                UserMission.user_id == user_id,
                UserMission.status == MissionStatus.PENDING,
            )
        )
        pending = result.scalar_one_or_none()
        if pending:
            return {
                "mission_id": pending.id,
                "is_newbie": is_newbie,
                "difficulty": "easy" if is_newbie else "medium",
                "slots": 1 if is_newbie else 2,
                "reward_influence": 3,
                "reward_money": 50 if is_newbie else 100,
                "fail_penalty": 5 if is_newbie else 7,
            }

        # Создаём возвратную миссию
        user_mission = await user_mission_crud.create(
            self.session,
            {
                "user_id": user_id,
                "mission_id": None,
                "status": MissionStatus.PENDING,
                "started_at": None,
                "ends_at": None,
                "success_chance": 100,
                "reward_money": 50 if is_newbie else 100,
                "reward_influence": 3,
                "wanted_increase": 0,
            },
        )

        return {
            "mission_id": user_mission.id,
            "is_newbie": is_newbie,
            "difficulty": "easy" if is_newbie else "medium",
            "slots": 1 if is_newbie else 2,
            "reward_influence": 3,
            "reward_money": 50 if is_newbie else 100,
            "fail_penalty": 5 if is_newbie else 7,
        }

    async def complete_return_mission(
        self, user_mission_id: int, user_id: int, success: bool
    ) -> dict:
        """Завершить возвратную миссию с наградой/штрафом."""
        user_mission = await user_mission_crud.get(self.session, user_mission_id)
        if not user_mission:
            return {"success": False, "message": "Миссия не найдена"}

        if user_mission.user_id != user_id:
            return {"success": False, "message": "Не ваша миссия"}

        is_newbie = await self._check_newbie(user_id)

        if success:
            user_mission.status = MissionStatus.COMPLETED
            user_mission.result = {"success": True, "type": "return"}

            resources = await user_resource_crud.get_by_user(self.session, user_id)
            if resources:
                resources.money += 50 if is_newbie else 100
                resources.influence += 3
        else:
            user_mission.status = MissionStatus.FAILED
            user_mission.result = {"success": False, "type": "return"}

            resources = await user_resource_crud.get_by_user(self.session, user_id)
            if resources:
                resources.influence = max(
                    0, resources.influence - (5 if is_newbie else 7)
                )

        return {
            "success": success,
            "influence_change": 3 if success else -(5 if is_newbie else 7),
            "money_change": 50 if (success and is_newbie) else 100 if success else 0,
        }

    async def _check_newbie(self, user_id: int) -> bool:
        from crud.other_crud import user_crud

        user = await user_crud.get(self.session, user_id)
        return self.is_newbie(user) if user else True
