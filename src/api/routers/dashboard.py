"""TMA Dashboard Router."""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.dependencies import get_current_user, get_db
from core.database.models import (
    ShopItem,
    UserMission,
    UserResource,
)
from services.territory_service import TerritoryService

router = APIRouter(prefix="/tma", tags=["TMA"])


@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Aggregated dashboard data for the Mini App.
    1. Updates passive income.
    2. Refills map missions.
    3. Returns user state, missions, and territories.
    """
    user_id = current_user.id

    # TODO: Move passive income and refill to background tasks / separate endpoint
    # For now, just read data to avoid datetime issues

    # 3. Fetch Data

    # Resources
    resources_result = await session.execute(
        select(UserResource).where(UserResource.user_id == user_id)
    )
    resources = resources_result.scalar_one_or_none()
    resources_data = {
        "money": resources.money if resources else 0,
        "influence": resources.influence if resources else 0,
        "wanted_level": resources.wanted_level if resources else 0,
        "active_playtime_minutes": (
            resources.active_playtime_minutes if resources else 0
        ),
        "last_income_tick": (
            resources.last_income_tick if resources else datetime.now(timezone.utc)
        ),
    }

    # Missions (Available/Pending and Active/In Progress)
    missions_result = await session.execute(
        select(UserMission)
        .options(selectinload(UserMission.mission))
        .where(UserMission.user_id == user_id)
        .order_by(UserMission.status, UserMission.created_at)
    )
    user_missions = missions_result.scalars().all()

    available_missions = []
    active_missions = []

    for um in user_missions:
        mission_data = {
            "id": um.id,
            "mission_id": um.mission_id,
            "status": um.status.value,
            "available_until": um.available_until,
            "location_name": um.location_name,
            "position_x": um.position_x,
            "position_y": um.position_y,
            "ends_at": um.ends_at,
            "reward_money": um.reward_money,
            # Template data
            "template_name": um.mission.name if um.mission else "Unknown",
            "template_description": um.mission.description if um.mission else "",
            "difficulty": um.mission.difficulty.value if um.mission else "unknown",
        }

        if um.status.value == "pending":
            available_missions.append(mission_data)
        elif um.status.value == "in_progress":
            active_missions.append(mission_data)

    # Territories — все территории со статусом
    territory_svc = TerritoryService(session)
    territories = await territory_svc.list_for_user(
        user_id, resources_data["influence"]
    )

    # Shop
    shop_result = await session.execute(
        select(ShopItem)
        .where(ShopItem.is_available.is_(True))
        .order_by(ShopItem.display_order)
    )
    shop_items = shop_result.scalars().all()
    shop = []
    for item in shop_items:
        shop.append(
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "item_type": item.item_type.value,
                "cost_money": item.cost_money,
                "cost_influence": item.cost_influence,
                "base_power": item.base_power,
                "bonus_power": item.bonus_power,
            }
        )

    return {
        "user_id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "resources": resources_data,
        "available_missions": available_missions,
        "active_missions": active_missions,
        "territories": territories,
        "shop": shop,
    }
