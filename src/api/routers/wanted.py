"""Wanted Level Router.

Endpoints for wanted level status and cooldown.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from crud.other_crud import user_resource_crud

router = APIRouter(prefix="/wanted", tags=["Wanted"])


@router.get("/status")
async def get_wanted_status(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get current wanted level and cooldown status."""
    resources = await user_resource_crud.get_by_user(session, current_user.id)
    wanted_level = resources.wanted_level if resources else 0

    is_blocked = wanted_level > 80
    cooldown_remaining = None  # TODO: implement cooldown tracking

    return {
        "wanted_level": wanted_level,
        "is_blocked": is_blocked,
        "cooldown_remaining": cooldown_remaining,
        "warning_threshold": 80,
    }


@router.post("/cooldown")
async def apply_cooldown(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Reduce wanted level (cooldown)."""
    resources = await user_resource_crud.get_by_user(session, current_user.id)
    if not resources:
        raise HTTPException(status_code=404, detail="User resources not found")

    # Simple cooldown: reduce wanted level by 5 (minimum 0)
    new_wanted = max(0, resources.wanted_level - 5)
    resources.wanted_level = new_wanted
    await session.commit()

    return {
        "wanted_level": new_wanted,
        "reduction": resources.wanted_level - new_wanted,
        "message": "Wanted level reduced",
    }
