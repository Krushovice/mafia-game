from pydantic import BaseModel


class WeaponCreate(BaseModel):
    name: str
    bonus_power: int
    owner_id: int

class ToolCreate(BaseModel):
    name: str
    bonus_intellect: int = 0
    bonus_agility: int = 0
    owner_id: int