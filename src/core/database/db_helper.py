from asyncio import current_task
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings
from core.database.models import Base


class DataBaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.engine = create_async_engine(
            url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self._session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def get_scoped_session(self) -> async_scoped_session:
        """
        Возвращает scoped session для текущей задачи asyncio.
        """
        return async_scoped_session(
            session_factory=self._session_factory,
            scopefunc=current_task,
        )

    async def session_dependency(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency.
        """
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.close()


# Инициализация для всего проекта
db_helper = DataBaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)


async def create_tables():
    """
    Создаёт все таблицы, используя метаданные Base.
    """
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
