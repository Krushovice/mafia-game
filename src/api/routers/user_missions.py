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


@router.get("/", response_model=list[UserMissionRead])
async def list_user_missions(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ums = await user_mission_crud.list_by_user(session, current_user.id)
    return ums


@router.get("/{um_id}/active_event", response_model=ActiveEventRead | None)
async def get_active_event(
    um_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get current active event that requires player choice."""
    svc = MissionService(session)
    result = await svc.get_active_event(um_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="No active event for this mission")
    return result


@router.post("/{um_id}/respond_event")
async def respond_event(
    um_id: int,
    body: EventChoiceResponse,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Respond to an active event with a choice."""
    svc = MissionService(session)
    res = await svc.respond_event(um_id, current_user.id, body.choice_type)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.post("/{um_id}/complete")
async def force_complete(
    um_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = MissionService(session)
    res = await svc.complete_mission(um_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res
