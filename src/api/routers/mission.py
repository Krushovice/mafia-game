from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from crud.other_crud import mission_event_crud
from schemas.mission_event_schemas import MissionEventCreate, MissionEventRead
from schemas.mission_schemas import MissionCreate, MissionRead
from schemas.user_mission_schemas import UserMissionRead, UserMissionStart
from services.mission_service import MissionService

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.post("/", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
async def create_mission(
    data: MissionCreate,
    session: AsyncSession = Depends(get_db),
):
    service = MissionService(session)
    return await service.create(data.model_dump())


@router.get("/{mission_id}", response_model=MissionRead)
async def get_mission(
    mission_id: int,
    session: AsyncSession = Depends(get_db),
):
    service = MissionService(session)
    mission = await service.get(mission_id)

    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    return mission


@router.post("/{mission_id}/events", response_model=MissionEventRead, status_code=201)
async def create_event(mission_id: int, data: MissionEventCreate, session: AsyncSession = Depends(get_db)):
    # create event linked to mission
    payload = data.model_dump()
    payload["mission_id"] = mission_id
    ev = await mission_event_crud.create(session, payload)
    return ev


@router.get("/{mission_id}/events", response_model=list[MissionEventRead])
async def list_events(mission_id: int, session: AsyncSession = Depends(get_db)):
    evs = await mission_event_crud.list_by_mission(session, mission_id)
    return evs


@router.post("/{mission_id}/start", response_model=UserMissionRead)
async def start_mission(mission_id: int, body: UserMissionStart, session: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    svc = MissionService(session)
    # load characters for validation
    from crud.other_crud import character_crud
    chars = []
    for cid in body.character_ids:
        c = await character_crud.get(session, cid)
        if not c:
            raise HTTPException(status_code=404, detail=f"Character {cid} not found")
        chars.append(c)

    res = await svc.start_mission(current_user.id, mission_id, chars)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))

    # return created user mission
    from crud.other_crud import user_mission_crud
    um = await user_mission_crud.get(session, res["mission_id"])
    return um


@router.get("/", response_model=list[MissionRead])
async def list_missions(session: AsyncSession = Depends(get_db)):
    from crud.other_crud import mission_crud
    missions = await mission_crud.list_with_events(session)
    return missions
