"""Schemas for shop items."""

from pydantic import BaseModel

from core.database.models.enums import ShopItemType


class ShopItemRead(BaseModel):
    id: int
    name: str
    description: str
    item_type: ShopItemType
    cost_money: int
    cost_influence: int
    role: str | None = None
    base_power: int
    base_intellect: int
    base_agility: int
    bonus_power: int
    bonus_intellect: int
    bonus_agility: int

    class Config:
        orm_mode = True
