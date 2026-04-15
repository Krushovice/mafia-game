"""Territory service — захват территорий и пассивный доход."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models.enums import MissionStatus
from crud.other_crud import (
    character_crud,
    territory_crud,
    user_mission_crud,
    user_resource_crud,
    user_territory_crud,
)

from .base_service import BaseService


class TerritoryService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, territory_crud)
        self.user_territory_crud = user_territory_crud
        self.user_resource_crud = user_resource_crud

    async def list_for_user(self, user_id: int, user_influence: int) -> list[dict]:
        """Список территорий со статусом для пользователя."""
        all_territories = await territory_crud.list_ordered(self.session)
        captured_ids = {
            ut.territory_id
            for ut in await self.user_territory_crud.list_by_user(self.session, user_id)
        }

        result = []
        for t in all_territories:
            is_captured = t.id in captured_ids
            can_attempt = user_influence >= t.influence_required and not is_captured
            result.append(
                {
                    "id": t.id,
                    "name": t.name,
                    "territory_type": t.territory_type.value,
                    "description": t.description,
                    "influence_required": t.influence_required,
                    "can_attempt": can_attempt,
                    "is_captured": is_captured,
                    "passive_income_money": t.passive_income_money,
                    "passive_income_influence": t.passive_income_influence,
                    "reward_influence": t.reward_influence,
                    "reward_money": t.reward_money,
                    "power_required": t.power_required,
                    "intellect_required": t.intellect_required,
                    "agility_required": t.agility_required,
                }
            )
        return result

    async def start_capture(
        self, user_id: int, territory_id: int, character_ids: list[int]
    ) -> dict:
        """Начать миссию захвата территории."""
        territory = await territory_crud.get(self.session, territory_id)
        if not territory:
            return {
                "success": False,
                "message": "Территория не найдена",
            }

        # Проверка влияния
        resources = await self.user_resource_crud.get_by_user(self.session, user_id)
        if not resources or resources.influence < territory.influence_required:
            return {
                "success": False,
                "message": f"Нужно {territory.influence_required} влияния для захвата",
            }

        # Проверка — не захвачена ли уже
        if await self.user_territory_crud.is_captured(
            self.session, user_id, territory_id
        ):
            return {
                "success": False,
                "message": "Территория уже захвачена",
            }

        # Проверка персонажей
        characters = []
        for cid in character_ids:
            c = await character_crud.get(self.session, cid)
            if not c:
                return {
                    "success": False,
                    "message": f"Персонаж {cid} не найден",
                }
            if c.is_busy:
                return {
                    "success": False,
                    "message": f"Персонаж {c.name} занят",
                }
            characters.append(c)

        if len(characters) != 3:
            return {
                "success": False,
                "message": "Для захвата нужно ровно 3 персонажа",
            }

        # Проверка статов
        total_power = sum(c.power for c in characters)
        total_intellect = sum(c.intellect for c in characters)
        total_agility = sum(c.agility for c in characters)

        if total_power < territory.power_required:
            return {
                "success": False,
                "message": f"Нужно {territory.power_required} силы, есть {total_power}",
            }
        if total_intellect < territory.intellect_required:
            return {
                "success": False,
                "message": f"Нужно {territory.intellect_required} интеллекта, есть {total_intellect}",
            }
        if total_agility < territory.agility_required:
            return {
                "success": False,
                "message": f"Нужно {territory.agility_required} ловкости, есть {total_agility}",
            }

        # Создаём миссию захвата (hard, 3 слота, duration = 5 минут для теста)
        duration = 300  # 5 минут

        if self.session.in_transaction():
            for c in characters:
                c.is_busy = True

            user_mission = await user_mission_crud.create(
                self.session,
                {
                    "user_id": user_id,
                    "mission_id": None,  # territory mission без привязки к missions
                    "status": MissionStatus.IN_PROGRESS,
                    "started_at": datetime.utcnow(),
                    "ends_at": datetime.utcnow() + timedelta(seconds=duration),
                    "success_chance": 100,
                    "reward_money": territory.reward_money,
                    "reward_influence": territory.reward_influence,
                    "wanted_increase": 12,  # hard
                },
                commit=False,
            )
            await self.session.flush()

            # Связываем персонажей
            from crud.other_crud import mission_character_crud

            for idx, c in enumerate(characters):
                await mission_character_crud.create_link(
                    self.session,
                    user_mission.id,
                    c.id,
                    idx,
                    commit=False,
                )
        else:
            async with self.session.begin():
                for c in characters:
                    c.is_busy = True

                user_mission = await user_mission_crud.create(
                    self.session,
                    {
                        "user_id": user_id,
                        "mission_id": None,
                        "status": MissionStatus.IN_PROGRESS,
                        "started_at": datetime.utcnow(),
                        "ends_at": datetime.utcnow() + timedelta(seconds=duration),
                        "success_chance": 100,
                        "reward_money": territory.reward_money,
                        "reward_influence": territory.reward_influence,
                        "wanted_increase": 12,
                    },
                    commit=False,
                )
                await self.session.flush()

                from crud.other_crud import mission_character_crud

                for idx, c in enumerate(characters):
                    await mission_character_crud.create_link(
                        self.session,
                        user_mission.id,
                        c.id,
                        idx,
                        commit=False,
                    )

        return {
            "success": True,
            "message": "Захват территории начат",
            "mission_id": user_mission.id,
            "territory_id": territory_id,
            "ends_at": user_mission.ends_at,
        }

    async def on_capture_complete(self, user_id: int, territory_id: int) -> bool:
        """Привязать территорию к пользователю после успешного захвата."""
        # Проверка — может уже захвачена (двойной вызов)
        if await self.user_territory_crud.is_captured(
            self.session, user_id, territory_id
        ):
            return True

        await self.user_territory_crud.create(
            self.session,
            {"user_id": user_id, "territory_id": territory_id},
            commit=False,
        )
        return True

    async def collect_passive_income(self, user_id: int) -> dict:
        """Calculate and apply passive income based on time passed.

        Online: Full income + influence accumulation.
        Offline (>15 min gap): Reduced income (5%), no influence.
        """
        from crud.other_crud import user_resource_crud, user_territory_crud

        resources = await user_resource_crud.get_by_user(self.session, user_id)
        if not resources:
            return {"money_gained": 0, "influence_gained": 0}

        # Get territories
        user_territories = await user_territory_crud.list_by_user(self.session, user_id)
        if not user_territories:
            return {"money_gained": 0, "influence_gained": 0}

        # Total income per tick (10 min)
        total_income_per_tick = sum(
            ut.territory.passive_income_money for ut in user_territories
        )
        influence_per_cycle = 0.2 + (0.1 * len(user_territories))

        now = datetime.now(timezone.utc)
        last_tick = resources.last_income_tick

        # Make last_tick timezone aware if naive
        if last_tick.tzinfo is None:
            last_tick = last_tick.replace(tzinfo=timezone.utc)

        delta = now - last_tick
        minutes_passed = delta.total_seconds() / 60.0

        # Cap offline time to 24 hours to prevent breaking economy
        if minutes_passed > 24 * 60:
            minutes_passed = 24 * 60
            now = last_tick + timedelta(minutes=minutes_passed)

        money_gained = 0
        influence_gained = 0

        if minutes_passed < 15:
            # --- ONLINE ---
            # Count towards playtime
            resources.active_playtime_minutes += minutes_passed

            # Calculate income: (minutes / 10) * rate
            ticks = minutes_passed / 10.0
            money_gained = int(ticks * total_income_per_tick)

            # Check influence reward (every 2 hours / 120 mins)
            if resources.active_playtime_minutes >= 120:
                influence_gained = influence_per_cycle
                resources.influence += influence_gained
                resources.active_playtime_minutes -= 120
        else:
            # --- OFFLINE ---
            # Reset playtime? No, keep it or decay it? Let's keep it.
            # Calculate income with 5% rate
            ticks = minutes_passed / 10.0
            money_gained = int(ticks * total_income_per_tick * 0.05)

        if money_gained > 0:
            resources.money += money_gained

        # Update tick time
        resources.last_income_tick = now
        resources.updated_at = now

        return {
            "money_gained": money_gained,
            "influence_gained": influence_gained,
            "active_playtime": resources.active_playtime_minutes,
            "total_income_per_tick": total_income_per_tick,
        }
