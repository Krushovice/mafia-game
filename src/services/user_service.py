from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .base_service import BaseService
from crud.other_crud import user_crud, user_resource_crud


class UserService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, user_crud)
        self.user_resource_crud = user_resource_crud

    async def create_user(self, data: dict):
        # create user within a transaction (start only if not already in one)
        if self.session.in_transaction():
            user = await self.crud.create(self.session, data, commit=False)
            await self.session.flush()
            return user
        else:
            async with self.session.begin():
                user = await self.crud.create(self.session, data, commit=False)
                await self.session.flush()
                return user
    async def get_by_telegram(self, telegram_id: int):
        return await self.crud.get_by_telegram(self.session, telegram_id)

    async def get_resources(self, user_id: int) -> Optional[dict]:
        res = await self.user_resource_crud.get_by_user(self.session, user_id)
        return res

    async def ensure_resources(self, user_id: int, defaults: dict):
        res = await self.user_resource_crud.get_by_user(self.session, user_id)
        if not res:
            if self.session.in_transaction():
                res = await self.user_resource_crud.create(self.session, {"user_id": user_id, **defaults}, commit=False)
                await self.session.flush()
                return res
            else:
                async with self.session.begin():
                    res = await self.user_resource_crud.create(self.session, {"user_id": user_id, **defaults}, commit=False)
                    await self.session.flush()
                    return res
        return res

    async def get_or_create_by_telegram(self, telegram_id: int, username: str | None = None):
        user = await self.get_by_telegram(telegram_id)
        if user:
            return user
        if self.session.in_transaction():
            user = await self.crud.create(self.session, {"telegram_id": telegram_id, "username": username}, commit=False)
            await self.session.flush()
            await self.user_resource_crud.create(self.session, {"user_id": user.id, "money": 1000, "influence": 10, "wanted_level": 0}, commit=False)
            return user
        else:
            async with self.session.begin():
                user = await self.crud.create(self.session, {"telegram_id": telegram_id, "username": username}, commit=False)
                await self.session.flush()
                await self.user_resource_crud.create(self.session, {"user_id": user.id, "money": 1000, "influence": 10, "wanted_level": 0}, commit=False)
                return user
