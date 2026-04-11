from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from crud.other_crud import user_mission_crud
from schemas.event_choice_schemas import (
    ActiveEventRead,
    EventChoiceResponse,
)
from schemas.user_mission_schemas import UserMissionRead
from services.mission_service import MissionService

router = APIRouter(prefix="/user_missions", tags=["UserMissions"])


@router.get(
    "/",
    response_model=list[UserMissionRead],
)
async def list_user_missions(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_missions = await user_mission_crud.list_by_user(session, current_user.id)
    return user_missions


@router.get(
    "/{mission_id}/active_event",
    response_model=ActiveEventRead | None,
)
async def get_active_event(
    mission_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get current active event that requires player choice."""
    service = MissionService(session)
    result = await service.get_active_event(mission_id, current_user.id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No active event for this mission",
        )
    return result


@router.post("/{mission_id}/respond_event")
async def respond_event(
    mission_id: int,
    body: EventChoiceResponse,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Respond to an active event with a choice."""
    service = MissionService(session)
    result = await service.respond_event(mission_id, current_user.id, body.choice_type)
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result


@router.post("/{mission_id}/complete")
async def complete_mission(
    mission_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = MissionService(session)
    result = await service.complete_mission(mission_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result
