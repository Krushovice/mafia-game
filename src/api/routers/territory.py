from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from crud.other_crud import (
    user_resource_crud,
    user_territory_crud,
)
from services.influence_decay_service import InfluenceDecayService
from services.territory_service import TerritoryService

router = APIRouter(prefix="/territories", tags=["Territories"])


@router.get("/")
async def list_territories(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Список территорий со статусом для текущего пользователя."""
    resources = await user_resource_crud.get_by_user(session, current_user.id)
    influence = resources.influence if resources else 0

    service = TerritoryService(session)
    return await service.list_for_user(current_user.id, influence)


@router.get("/income")
async def get_passive_income(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Текущий пассивный доход от территорий."""
    return await user_territory_crud.get_total_passive_income(session, current_user.id)


@router.post("/{territory_id}/capture")
async def start_capture(
    territory_id: int,
    character_ids: list[int],
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Начать миссию захвата территории."""
    service = TerritoryService(session)
    result = await service.start_capture(current_user.id, territory_id, character_ids)
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result


@router.post("/return_mission")
async def get_return_mission(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Получить возвратную миссию после долгого отсутствия."""
    from services.user_service import UserService

    decay_service = InfluenceDecayService(session)
    user = await UserService(session).get(current_user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    is_newbie = decay_service.is_newbie(user)
    mission = await decay_service.get_or_create_return_mission(
        current_user.id, is_newbie
    )
    if not mission:
        raise HTTPException(
            status_code=404,
            detail="No return mission available",
        )
    return mission


@router.post("/return_mission/{mission_id}/complete")
async def complete_return_mission(
    mission_id: int,
    success: bool,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Завершить возвратную миссию."""
    decay_service = InfluenceDecayService(session)
    result = await decay_service.complete_return_mission(
        mission_id, current_user.id, success
    )
    if not result.get("success") and "message" in result:
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result


@router.get("/decay")
async def check_decay(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Проверить decay влияния при входе."""
    from services.user_service import UserService

    decay_service = InfluenceDecayService(session)
    user = await UserService(session).get(current_user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return await decay_service.apply_decay(current_user.id)
