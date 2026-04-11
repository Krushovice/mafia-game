from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from api.routers import character as character_router
from api.routers import equipment as equipment_router
from api.routers import mission as mission_router
from api.routers import territory as territory_router
from api.routers import user as user_router
from api.routers import user_missions as user_missions_router
from core.config import settings
from core.database.db_helper import db_helper
from core.logging import setup_logging

# Configure logging from settings
setup_logging(level=settings.logging.level, fmt=settings.logging.fmt)

app = FastAPI(
    title=settings.api.title,
    debug=settings.api.debug,
    root_path=settings.api.root_path,
)

# CORS for Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(mission_router.router)
app.include_router(character_router.router)
app.include_router(user_router.router)
app.include_router(user_missions_router.router)
app.include_router(equipment_router.router)
app.include_router(territory_router.router)


# Session dependency (routers use `api.dependencies.get_db`)
async def get_session() -> AsyncSession:
    async for session in db_helper.session_dependency():
        yield session
