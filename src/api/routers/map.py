"""Map Router — отдаёт карту города с территориями и NPC боссами."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.dependencies import get_current_user, get_db
from core.database.models import Territory, NPCBoss, UserTerritory

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/")
async def get_map(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Карта города: территории + NPC боссы + статус пользователя."""
    # Get user's captured territories
    user_ter_result = await session.execute(
        select(UserTerritory).where(UserTerritory.user_id == current_user.id)
    )
    user_territory_ids = {ut.territory_id for ut in user_ter_result.scalars().all()}

    # Get all territories with boss info
    result = await session.execute(
        select(Territory)
        .options(selectinload(Territory.boss))
        .order_by(Territory.display_order)
    )
    territories = result.scalars().all()

    map_data = []
    for t in territories:
        is_mine = t.id in user_territory_ids
        boss_data = None
        if t.boss:
            boss_data = {
                "id": t.boss.id,
                "name": t.boss.name,
                "color": t.boss.color,
                "influence": t.boss.influence,
                "power": t.boss.power,
            }

        map_data.append(
            {
                "id": t.id,
                "name": t.name,
                "territory_type": t.territory_type.value,
                "description": t.description,
                "grid_x": t.grid_x,
                "grid_y": t.grid_y,
                "influence_required": t.influence_required,
                "power_required": t.power_required,
                "intellect_required": t.intellect_required,
                "agility_required": t.agility_required,
                "passive_income_money": t.passive_income_money,
                "passive_income_influence": t.passive_income_influence,
                "reward_influence": t.reward_influence,
                "reward_money": t.reward_money,
                "is_mine": is_mine,
                "boss": boss_data,
            }
        )

    return {"territories": map_data}
