"""Schemas for mission event choices and event response."""

from pydantic import BaseModel

from core.database.models.enums import EventChoiceType


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
    """Ответ игрока на событие."""
    choice_type: EventChoiceType


class ActiveEventRead(BaseModel):
    """Текущее активное событие миссии."""
    event_log_id: int
    event_type: str
    event_description: str
    choices: list[MissionEventChoiceRead] = []

    class Config:
        orm_mode = True
