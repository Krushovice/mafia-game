from datetime import datetime

from pydantic import BaseModel

from core.database.models.enums import MissionStatus


class MissionCharacterRead(BaseModel):
    id: int
    user_mission_id: int
    character_id: int
    slot_number: int

    class Config:
        orm_mode = True


class UserMissionRead(BaseModel):
    id: int
    user_id: int
    mission_id: int
    status: MissionStatus
    started_at: datetime | None
    ends_at: datetime | None
    success_chance: int | None
    result: dict | None = None
    characters: list[MissionCharacterRead] = []

    class Config:
        orm_mode = True


class UserMissionStart(BaseModel):
    character_ids: list[int]
