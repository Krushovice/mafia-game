import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.core.config import settings
from src.core.database.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Настраиваем логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata всех моделей
target_metadata = Base.metadata

# ----------------------------------------------------------
# Функции миграции
# ----------------------------------------------------------

def do_run_migrations(connection):
    """Sync runner, вызывается внутри run_sync."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Основной async runner для Alembic + asyncpg."""
    # создаём engine прямо из settings
    connectable: AsyncEngine = create_async_engine(
        settings.db.url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Запуск миграций в онлайн режиме через asyncio."""
    asyncio.run(run_async_migrations())


def run_migrations_offline():
    """Offline mode — оставим для совместимости."""
    url = str(settings.db.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ----------------------------------------------------------
# Основной entrypoint
# ----------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()