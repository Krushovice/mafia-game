from src.core.config import settings
from src.core.database.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(str(settings.db.url))

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

import asyncio
if __name__ == "__main__":
    asyncio.run(create_tables())


