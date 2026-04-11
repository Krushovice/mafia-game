from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models.enums import CharacterRole, CharacterTrait
from crud.other_crud import (
    character_crud,
    user_crud,
    user_resource_crud,
)

from .base_service import BaseService


class UserService(BaseService):
    # Стартовые ресурсы
    STARTER_MONEY = 1000
    STARTER_INFLUENCE = 10
    STARTER_WANTED = 0

    # Стартовый персонаж — универсальный капо
    STARTER_CHAR_NAME = "Капо"
    STARTER_CHAR_ROLE = CharacterRole.CAPO
    STARTER_CHAR_TRAIT = CharacterTrait.QUIET
    STARTER_CHAR_POWER = 10
    STARTER_CHAR_INTELLECT = 10
    STARTER_CHAR_AGILITY = 10
    STARTER_CHAR_LOYALTY = 10

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
                res = await self.user_resource_crud.create(
                    self.session,
                    {"user_id": user_id, **defaults},
                    commit=False,
                )
                await self.session.flush()
                return res
            else:
                async with self.session.begin():
                    res = await self.user_resource_crud.create(
                        self.session,
                        {"user_id": user_id, **defaults},
                        commit=False,
                    )
                    await self.session.flush()
                    return res
        return res

    async def _create_starter_package(self, user_id: int):
        """Создать стартовый пакет: ресурсы + 1 капо."""
        # Ресурсы
        await self.user_resource_crud.create(
            self.session,
            {
                "user_id": user_id,
                "money": self.STARTER_MONEY,
                "influence": self.STARTER_INFLUENCE,
                "wanted_level": self.STARTER_WANTED,
            },
            commit=False,
        )
        # Стартовый персонаж
        await character_crud.create(
            self.session,
            {
                "user_id": user_id,
                "name": self.STARTER_CHAR_NAME,
                "role": self.STARTER_CHAR_ROLE,
                "trait": self.STARTER_CHAR_TRAIT,
                "power": self.STARTER_CHAR_POWER,
                "intellect": self.STARTER_CHAR_INTELLECT,
                "agility": self.STARTER_CHAR_AGILITY,
                "loyalty": self.STARTER_CHAR_LOYALTY,
                "is_busy": False,
            },
            commit=False,
        )

    async def get_or_create_by_telegram(
        self, telegram_id: int, username: str | None = None
    ):
        user = await self.get_by_telegram(telegram_id)
        if user:
            return user
        if self.session.in_transaction():
            user = await self.crud.create(
                self.session,
                {"telegram_id": telegram_id, "username": username},
                commit=False,
            )
            await self.session.flush()
            await self._create_starter_package(user.id)
            return user
        else:
            async with self.session.begin():
                user = await self.crud.create(
                    self.session,
                    {"telegram_id": telegram_id, "username": username},
                    commit=False,
                )
                await self.session.flush()
                await self._create_starter_package(user.id)
                return user
