from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.database.models import Character, Weapon, Tool, Mission, MissionEvent
from .base_crud import CRUDBase

# ---------------------------------------------------
# 🔹 Character CRUD
# ---------------------------------------------------
class CRUDCharacter(CRUDBase[Character]):
    async def list_with_equipment(self, session: AsyncSession) -> List[Character]:
        result = await session.execute(
            select(Character).options(selectinload(Character.weapons), selectinload(Character.tools))
        )
        return result.scalars().all()

# ---------------------------------------------------
# 🔹 Weapon CRUD
# ---------------------------------------------------
class CRUDWeapon(CRUDBase[Weapon]):
    async def list_by_owner(self, session: AsyncSession, owner_id: int) -> List[Weapon]:
        result = await session.execute(select(Weapon).where(Weapon.owner_id == owner_id))
        return result.scalars().all()

# ---------------------------------------------------
# 🔹 Tool CRUD
# ---------------------------------------------------
class CRUDTool(CRUDBase[Tool]):
    async def list_by_owner(self, session: AsyncSession, owner_id: int) -> List[Tool]:
        result = await session.execute(select(Tool).where(Tool.owner_id == owner_id))
        return result.scalars().all()

# ---------------------------------------------------
# 🔹 MissionEvent CRUD
# ---------------------------------------------------
class CRUDMissionEvent(CRUDBase[MissionEvent]):
    async def list_by_mission(self, session: AsyncSession, mission_id: int) -> List[MissionEvent]:
        result = await session.execute(select(MissionEvent).where(MissionEvent.mission_id == mission_id))
        return result.scalars().all()

# ---------------------------------------------------
# 🔹 Mission CRUD
# ---------------------------------------------------
class CRUDMission(CRUDBase[Mission]):
    async def list_with_events(self, session: AsyncSession) -> List[Mission]:
        result = await session.execute(select(Mission).options(selectinload(Mission.events)))
        return result.scalars().all()

    async def add_event(self, session: AsyncSession, mission_id: int, event_data: dict) -> MissionEvent:
        event = MissionEvent(**event_data, mission_id=mission_id)
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event