from typing import AsyncGenerator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.tma_auth import validate_init_data
from core.config import settings
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
        raise HTTPException(
            status_code=500,
            detail="Database session not provided to auth dependency",
        )
    if telegram_id is None:
        raise HTTPException(status_code=401, detail="X-Telegram-Id header required")
    svc = UserService(db)
    user = await svc.get_or_create_by_telegram(telegram_id, username)
    return user


async def get_current_user_tma(
    init_data: str = Header(..., alias="X-Telegram-InitData"),
    db: AsyncSession = Depends(lambda: None),
) -> object:
    """Resolve current user from Telegram WebApp initData.

    Validates the HMAC using the bot token from settings.
    """
    if db is None:
        raise HTTPException(
            status_code=500,
            detail="Database session not provided to auth dependency",
        )

    if not settings.tma or not settings.tma.bot_token:
        raise HTTPException(
            status_code=500,
            detail="TMA not configured (missing tma.bot_token)",
        )

    user_data = validate_init_data(init_data, settings.tma.bot_token)

    telegram_id = user_data.get("id")
    username = user_data.get("username")
    first_name = user_data.get("first_name", "")

    if not telegram_id:
        raise HTTPException(status_code=401, detail="No user id in initData")

    svc = UserService(db)
    user = await svc.get_or_create_by_telegram(telegram_id, username or first_name)

    # Passive income calculation
    from services.territory_service import TerritoryService

    territory_svc = TerritoryService(db)
    income = await territory_svc.collect_passive_income(user.id)
    # Note: Session commits happen at the end of request via dependency

    return user


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.session_dependency():
        yield session
