from sqlalchemy.ext.asyncio import AsyncSession

from crud.base_crud import CRUDBase


class BaseService:
    def __init__(self, session: AsyncSession, crud: CRUDBase):
        self.session = session
        self.crud = crud

    async def create(self, data: dict):
        return await self.crud.create(self.session, data)

    async def get(self, obj_id: int):
        return await self.crud.get(self.session, obj_id)

    async def get_all(self):
        return await self.crud.get_multi(self.session)

    async def update(self, obj_id: int, data: dict):
        return await self.crud.update(self.session, obj_id, data)

    async def delete(self, obj_id: int):
        return await self.crud.delete(self.session, obj_id)