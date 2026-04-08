from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from services.character_service import CharacterService
from schemas.character_schemas import CharacterCreate, CharacterRead
from schemas import UserRead

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post("/", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(
    data: CharacterCreate,
    session: AsyncSession = Depends(get_db),
    current_user = Depends(lambda db=Depends(get_db): get_current_user(db=db)),
):
    service = CharacterService(session)
    payload = data.model_dump()
    payload["user_id"] = current_user.id
    return await service.create(payload)


@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(
    character_id: int,
    session: AsyncSession = Depends(get_db),
):
    service = CharacterService(session)
    character = await service.get_character(character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return character



@router.patch("/{character_id}", response_model=CharacterRead)
async def update_character(
    character_id: int,
    data: dict,
    session: AsyncSession = Depends(get_db),
    current_user = Depends(lambda db=Depends(get_db): get_current_user(db=db)),
):
    service = CharacterService(session)
    existing = await service.get(character_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Character not found")
    if existing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    updated = await service.update(character_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Character not found")
    return updated
