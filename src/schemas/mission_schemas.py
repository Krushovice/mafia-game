from pydantic import BaseModel
from core.database.models.enums import MissionDifficulty

class MissionEventRead(BaseModel):
    id: int
    event_type: str
    chance: int
    description: str

    class Config:
        orm_mode = True

class MissionRead(BaseModel):
    id: int
    name: str
    description: str
    duration: int
    reward_money: int
    reward_influence: int
    difficulty: MissionDifficulty
    slots: int
    power_required: int
    intellect_required: int
    agility_required: int
    events: list[MissionEventRead] = []

    class Config:
        orm_mode = True

class MissionCreate(BaseModel):
    name: str
    description: str
    duration: int
    reward_money: int = 0
    reward_influence: int = 0
    difficulty: MissionDifficulty = MissionDifficulty.EASY
    slots: int = 1
    power_required: int = 0
    intellect_required: int = 0
    agility_required: int = 0