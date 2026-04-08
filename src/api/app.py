from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from api.routers import mission as mission_router
from api.routers import character as character_router
from api.routers import user as user_router
from api.routers import user_missions as user_missions_router
from api.routers import equipment as equipment_router

app = FastAPI()

# include routers
app.include_router(mission_router.router)
app.include_router(character_router.router)
app.include_router(user_router.router)
app.include_router(user_missions_router.router)
app.include_router(equipment_router.router)

# Session dependency (routers use `api.dependencies.get_db`)
async def get_session() -> AsyncSession:
    async for session in db_helper.session_dependency():
        yield session
