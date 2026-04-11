from pydantic import BaseModel

from core.database.models.enums import MissionEventType


class MissionEventCreate(BaseModel):
    mission_id: int
    event_type: MissionEventType
    chance: int = 10
    description: str = ""


class MissionEventRead(BaseModel):
    id: int
    mission_id: int
    event_type: str
    chance: int
    description: str

    class Config:
        orm_mode = True
