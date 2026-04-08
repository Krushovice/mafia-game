from sqlalchemy.ext.asyncio import AsyncSession

from crud.other_crud import character_crud
from schemas.character_schemas import CharacterCreate

from .base_service import BaseService


class CharacterService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, character_crud)

    async def create_character(self, data: CharacterCreate):
        # create character in a transaction and attach to session
        payload = data.model_dump()
        if self.session.in_transaction():
            char = await self.crud.create(self.session, payload, commit=False)
            await self.session.flush()
            return char
        else:
            async with self.session.begin():
                char = await self.crud.create(self.session, payload, commit=False)
                await self.session.flush()
                return char

    async def get_character(self, character_id: int):
        return await self.get(character_id)
