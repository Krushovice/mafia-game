from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from services.character import CharacterService
from schemas.character_schemas import CharacterCreate, CharacterRead

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post("/", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(
    data: CharacterCreate,
    session: AsyncSession = Depends(get_db),
):
    service = CharacterService(session)
    return await service.create_character(data)


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