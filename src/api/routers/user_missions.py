from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from services.mission_service import MissionService
from crud.other_crud import user_mission_crud
from schemas.user_mission_schemas import UserMissionRead

router = APIRouter(prefix="/user_missions", tags=["UserMissions"])


@router.get("/", response_model=list[UserMissionRead])
async def list_user_missions(session: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    ums = await user_mission_crud.list_by_user(session, current_user.id)
    return ums


@router.post("/{um_id}/complete")
async def force_complete(um_id: int, session: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    svc = MissionService(session)
    res = await svc.complete_mission(um_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res
