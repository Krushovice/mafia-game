from pydantic import BaseModel

from core.database.models.enums import MissionDifficulty, MissionStatType


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
    wanted_increase: int
    difficulty: MissionDifficulty
    mission_stat_type: MissionStatType
    slots: int
    power_required: int
    intellect_required: int
    agility_required: int
    weapon_slots_required: int
    tool_slots_required: int
    reward_multiplier: float
    events: list[MissionEventRead] = []

    class Config:
        orm_mode = True


class MissionCreate(BaseModel):
    name: str
    description: str
    duration: int
    difficulty: MissionDifficulty = MissionDifficulty.EASY
    mission_stat_type: MissionStatType = MissionStatType.FORCE
    slots: int = 1
    power_required: int = 0
    intellect_required: int = 0
    agility_required: int = 0
    weapon_slots_required: int = 0
    tool_slots_required: int = 0
    reward_multiplier: float = 1.0
