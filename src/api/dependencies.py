from typing import AsyncGenerator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from services.user_service import UserService


async def get_current_user(
    telegram_id: int | None = Header(None, convert_underscores=False),
    username: str | None = Header(None, convert_underscores=False),
    db: AsyncSession = Depends(lambda: None),
) -> object:
    """Resolve current user from `X-Telegram-Id` header. Returns ORM User."""
    # Note: callers should pass `db` via `Depends(get_db)` when using this dependency.
    if db is None:
        raise HTTPException(status_code=500, detail="Database session not provided to auth dependency")
    if telegram_id is None:
        raise HTTPException(status_code=401, detail="X-Telegram-Id header required")
    svc = UserService(db)
    user = await svc.get_or_create_by_telegram(telegram_id, username)
    return user


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.session_dependency():
        yield session