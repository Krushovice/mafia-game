from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from crud.other_crud import (
    character_crud,
    user_mission_crud,
)
from schemas.event_choice_schemas import (
    EventChoiceResponse,
)
from schemas.user_mission_schemas import (
    UserMissionRead,
    UserMissionStart,
)
from services.mission_service import MissionService

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.get(
    "/",
    response_model=list[UserMissionRead],
)
async def list_missions(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get available missions on the user's map (refills if needed)."""
    service = MissionService(session)
    await service.refill_missions(current_user.id)

    missions = await user_mission_crud.list_by_user(session, current_user.id)
    return [m for m in missions if m.status == "pending"]


@router.post("/{mission_id}/start")
async def start_mission(
    mission_id: int,
    body: UserMissionStart,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Start execution of a mission from the map."""
    service = MissionService(session)

    characters = []
    for character_id in body.character_ids:
        character = await character_crud.get(session, character_id)
        if not character:
            raise HTTPException(
                status_code=404,
                detail=f"Character {character_id} not found",
            )
        characters.append(character)

    result = await service.start_mission_execution(
        current_user.id, mission_id, characters
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result


@router.get("/{mission_id}/events", response_model=list[dict])
async def list_events(
    mission_id: int,
    session: AsyncSession = Depends(get_db),
):
    """List events for a mission template (for info)."""
    from crud.other_crud import mission_event_crud

    events = await mission_event_crud.list_by_mission(session, mission_id)
    return events


@router.post("/{mission_id}/respond_event")
async def respond_event(
    mission_id: int,
    body: EventChoiceResponse,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Respond to an active event."""
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
    """Force complete a mission (admin/debug or timer finished)."""
    service = MissionService(session)
    result = await service.complete_mission(mission_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result
