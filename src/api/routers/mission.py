from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from services.mission_service import MissionService
from schemas.mission_schemas import MissionCreate, MissionRead

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.post("/", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
async def create_mission(
    data: MissionCreate,
    session: AsyncSession = Depends(get_db),
):
    service = MissionService()
    return await service.create_mission(session=session, data)


@router.get("/{mission_id}", response_model=MissionRead)
async def get_mission(
    mission_id: int,
    session: AsyncSession = Depends(get_db),
):
    service = MissionService(session)
    mission = await service.get_mission(mission_id)

    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    return mission