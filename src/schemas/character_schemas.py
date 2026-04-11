from typing import List

from pydantic import BaseModel


class WeaponRead(BaseModel):
    id: int
    name: str
    bonus_power: int

    class Config:
        orm_mode = True


class ToolRead(BaseModel):
    id: int
    name: str
    bonus_intellect: int
    bonus_agility: int

    class Config:
        orm_mode = True


class CharacterRead(BaseModel):
    id: int
    name: str
    power: int
    intellect: int
    agility: int
    is_busy: bool
    weapons: List[WeaponRead] = []
    tools: List[ToolRead] = []

    class Config:
        orm_mode = True


class CharacterCreate(BaseModel):
    name: str
    power: int
    intellect: int
    agility: int
