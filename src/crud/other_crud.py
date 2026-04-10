from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.database.models import (
    Character,
    Mission,
    MissionCharacter,
    MissionEvent,
    MissionEventChoice,
    Tool,
    User,
    UserMission,
    UserMissionEventLog,
    UserResource,
    Weapon,
)

from .base_crud import CRUDBase


# ---------------------------------------------------
# 🔹 Character CRUD
# ---------------------------------------------------
class CRUDCharacter(CRUDBase[Character]):
    def __init__(self):
        super().__init__(Character)

    async def list_with_equipment(self, session: AsyncSession) -> List[Character]:
        result = await session.execute(
            select(Character).options(
                selectinload(Character.weapons), selectinload(Character.tools)
            )
        )
        return result.scalars().all()

    async def list_by_user_with_equipment(
        self, session: AsyncSession, user_id: int
    ) -> List[Character]:
        result = await session.execute(
            select(Character)
            .where(Character.user_id == user_id)
            .options(selectinload(Character.weapons), selectinload(Character.tools))
        )
        return result.scalars().all()


# ---------------------------------------------------
# 🔹 Weapon CRUD
# ---------------------------------------------------
class CRUDWeapon(CRUDBase[Weapon]):
    def __init__(self):
        super().__init__(Weapon)

    async def list_by_owner(self, session: AsyncSession, owner_id: int) -> List[Weapon]:
        result = await session.execute(
            select(Weapon).where(Weapon.owner_id == owner_id)
        )
        return result.scalars().all()


# ---------------------------------------------------
# 🔹 Tool CRUD
# ---------------------------------------------------
class CRUDTool(CRUDBase[Tool]):
    def __init__(self):
        super().__init__(Tool)

    async def list_by_owner(self, session: AsyncSession, owner_id: int) -> List[Tool]:
        result = await session.execute(select(Tool).where(Tool.owner_id == owner_id))
        return result.scalars().all()


# ---------------------------------------------------
# 🔹 MissionEvent CRUD
# ---------------------------------------------------
class CRUDMissionEvent(CRUDBase[MissionEvent]):
    def __init__(self):
        super().__init__(MissionEvent)

    async def list_by_mission(
        self, session: AsyncSession, mission_id: int
    ) -> List[MissionEvent]:
        result = await session.execute(
            select(MissionEvent).where(MissionEvent.mission_id == mission_id)
        )
        return result.scalars().all()


# ---------------------------------------------------
# 🔹 Mission CRUD
# ---------------------------------------------------
class CRUDMission(CRUDBase[Mission]):
    def __init__(self):
        super().__init__(Mission)

    async def list_with_events(self, session: AsyncSession) -> List[Mission]:
        result = await session.execute(
            select(Mission).options(selectinload(Mission.events))
        )
        return result.scalars().all()

    async def add_event(
        self,
        session: AsyncSession,
        mission_id: int,
        event_data: dict,
        commit: bool = True,
    ) -> MissionEvent:
        event = MissionEvent(**event_data, mission_id=mission_id)
        session.add(event)
        if commit:
            await session.commit()
            await session.refresh(event)
        return event


# Module-level CRUD instances for convenient imports
character_crud = CRUDCharacter()
weapon_crud = CRUDWeapon()
tool_crud = CRUDTool()
mission_event_crud = CRUDMissionEvent()
mission_crud = CRUDMission()
mission_character_crud = None


# UserMission CRUD (basic)
class CRUDUserMission(CRUDBase[UserMission]):
    def __init__(self):
        super().__init__(UserMission)


# MissionCharacter CRUD
class CRUDMissionCharacter(CRUDBase[MissionCharacter]):
    def __init__(self):
        super().__init__(MissionCharacter)

    async def create_link(
        self,
        session: AsyncSession,
        user_mission_id: int,
        character_id: int,
        slot_number: int,
        commit: bool = True,
    ):
        obj = MissionCharacter(
            user_mission_id=user_mission_id,
            character_id=character_id,
            slot_number=slot_number,
        )
        session.add(obj)
        if commit:
            await session.commit()
            await session.refresh(obj)
        return obj


# expose instances
user_mission_crud = CRUDUserMission()
mission_character_crud = CRUDMissionCharacter()


# User CRUD
class CRUDUser(CRUDBase[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_telegram(
        self, session: AsyncSession, telegram_id: int
    ) -> User | None:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


# UserResource CRUD
class CRUDUserResource(CRUDBase[UserResource]):
    def __init__(self):
        super().__init__(UserResource)

    async def get_by_user(
        self, session: AsyncSession, user_id: int
    ) -> UserResource | None:
        result = await session.execute(
            select(UserResource).where(UserResource.user_id == user_id)
        )
        return result.scalar_one_or_none()


# expose instances
user_crud = CRUDUser()
user_resource_crud = CRUDUserResource()


# MissionEventChoice CRUD
class CRUDMissionEventChoice(CRUDBase[MissionEventChoice]):
    def __init__(self):
        super().__init__(MissionEventChoice)

    async def list_by_event(
        self, session: AsyncSession, event_id: int
    ) -> List[MissionEventChoice]:
        result = await session.execute(
            select(MissionEventChoice)
            .where(MissionEventChoice.event_id == event_id)
            .order_by(MissionEventChoice.id)
        )
        return result.scalars().all()


# UserMissionEventLog CRUD
class CRUDUserMissionEventLog(CRUDBase[UserMissionEventLog]):
    def __init__(self):
        super().__init__(UserMissionEventLog)

    async def get_active(
        self, session: AsyncSession, user_mission_id: int
    ) -> UserMissionEventLog | None:
        """Get unresolved event log for a user mission."""
        result = await session.execute(
            select(UserMissionEventLog).where(
                UserMissionEventLog.user_mission_id == user_mission_id,
                UserMissionEventLog.resolved == False,
            )
        )
        return result.scalar_one_or_none()


# expose instances
mission_event_choice_crud = CRUDMissionEventChoice()
user_mission_event_log_crud = CRUDUserMissionEventLog()
