from sqlalchemy.ext.asyncio import AsyncSession

from .base_service import BaseService
from crud.other_crud import CRUDCharacter
from schemas.character_schemas import CharacterCreate


class CharacterService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CRUDCharacter)

    async def create_character(self, data: CharacterCreate):
        return await self.create(data.model_dump())

    async def get_character(self, character_id: int):
        return await self.get(character_id)