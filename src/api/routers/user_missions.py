from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.dependencies import get_current_user, get_db
from core.database.models import Mission, MissionEvent
from core.database.models.mission_event_choice import MissionEventChoice
from crud.other_crud import user_mission_crud
from schemas.event_choice_schemas import (
    ActiveEventRead,
    EventChoiceResponse,
    MissionEventChoiceRead,
)
from schemas.user_mission_schemas import UserMissionRead, UserMissionStart
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


@router.get(
    "/{mission_id}/event_choices",
    response_model=list[MissionEventChoiceRead],
)
async def get_event_choices(
    mission_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all possible choices for events in this mission template."""
    # Get mission with events and choices
    mission_result = await session.execute(
        select(Mission)
        .options(selectinload(Mission.events).selectinload(MissionEvent.choices))
        .where(Mission.id == mission_id)
    )
    mission = mission_result.scalar_one_or_none()

    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    # Collect choices from all events
    all_choices = []
    for event in mission.events:
        if event.choices:
            for choice in event.choices:
                all_choices.append(
                    MissionEventChoiceRead(
                        id=choice.id,
                        event_id=choice.event_id,
                        choice_type=choice.choice_type.value,
                        label=choice.label,
                        description=choice.description,
                        money_cost=choice.money_cost,
                        influence_required=choice.influence_required,
                        power_required=choice.power_required,
                        success_chance_base=choice.success_chance_base,
                    )
                )

    return all_choices


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
