from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.session_dependency():
        yield session