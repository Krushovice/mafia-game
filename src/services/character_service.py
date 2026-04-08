from sqlalchemy.ext.asyncio import AsyncSession

from .base_service import BaseService
from crud.other_crud import character_crud
from schemas.character_schemas import CharacterCreate


class CharacterService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, character_crud)

    async def create_character(self, data: CharacterCreate):
        # create character in a transaction and attach to session
        payload = data.model_dump()
        async with self.session.begin():
            char = await self.crud.create(self.session, payload, commit=False)
            await self.session.flush()
            return char

    async def get_character(self, character_id: int):
        return await self.get(character_id)
