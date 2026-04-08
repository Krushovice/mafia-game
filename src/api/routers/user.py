from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from services.user_service import UserService
from schemas import UserRead, UserResourceRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(telegram_id: int, username: str | None = None, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    user = await service.create_user({"telegram_id": telegram_id, "username": username})
    # ensure resources
    await service.ensure_resources(user.id, {"money": 1000, "influence": 10, "wanted_level": 0})
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    user = await service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/resources", response_model=UserResourceRead)
async def get_resources(user_id: int, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    res = await service.get_resources(user_id)
    if not res:
        raise HTTPException(status_code=404, detail="Resources not found")
    return res
