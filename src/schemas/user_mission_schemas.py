"""Schemas for mission events and responses."""

from pydantic import BaseModel

from core.database.models.enums import EventChoiceType, MissionStatus


class MissionEventChoiceRead(BaseModel):
    id: int
    event_id: int
    choice_type: EventChoiceType
    label: str
    description: str
    money_cost: int
    influence_required: int
    power_required: int
    success_chance_base: int

    class Config:
        orm_mode = True


class EventChoiceResponse(BaseModel):
    """Response body for player choice."""

    choice_type: EventChoiceType


class ActiveEventRead(BaseModel):
    """Current active event requiring choice."""

    event_log_id: int
    event_type: str
    event_description: str
    choices: list[MissionEventChoiceRead] = []

    class Config:
        orm_mode = True


class UserMissionRead(BaseModel):
    """Mission instance on the user's map."""

    id: int
    mission_id: int | None
    status: MissionStatus
    started_at: str | None
    ends_at: str | None
    available_until: str | None
    location_name: str
    position_x: int
    position_y: int
    success_chance: int
    reward_money: int | None
    reward_influence: int | None
    wanted_increase: int | None

    class Config:
        orm_mode = True


class UserMissionStart(BaseModel):
    """Payload to start a mission execution."""

    character_ids: list[int]
