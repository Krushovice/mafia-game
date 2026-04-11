"""Schemas for TMA Dashboard."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.database.models.enums import MissionStatus


class DashboardResources(BaseModel):
    money: int
    influence: int
    wanted_level: int
    active_playtime_minutes: float
    last_income_tick: Optional[datetime]

    class Config:
        orm_mode = True


class DashboardMission(BaseModel):
    id: int
    mission_id: Optional[int]  # Null for template missions on map
    status: MissionStatus
    available_until: Optional[datetime]
    location_name: Optional[str]
    position_x: Optional[int]
    position_y: Optional[int]
    
    # Template info (if available)
    template_name: Optional[str]
    template_description: Optional[str]
    difficulty: Optional[str]
    
    # Stats for running mission
    ends_at: Optional[datetime]
    reward_money: Optional[int]

    class Config:
        orm_mode = True


class DashboardTerritory(BaseModel):
    id: int
    name: str
    territory_type: str
    passive_income_money: int
    captured_at: Optional[datetime]

    class Config:
        orm_mode = True


class DashboardShopItem(BaseModel):
    id: int
    name: str
    description: str
    item_type: str
    cost_money: int
    cost_influence: int
    base_power: Optional[int]
    bonus_power: Optional[int]
    
    class Config:
        orm_mode = True


class DashboardResponse(BaseModel):
    user_id: int
    telegram_id: int
    username: Optional[str]
    
    resources: DashboardResources
    
    # Map missions (Pending)
    available_missions: list[DashboardMission]
    
    # Running missions (In Progress)
    active_missions: list[DashboardMission]
    
    # Captured territories
    territories: list[DashboardTerritory]
    
    # Shop items
    shop: list[DashboardShopItem]
