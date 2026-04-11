from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from api.routers import character as character_router
from api.routers import dashboard as dashboard_router
from api.routers import equipment as equipment_router
from api.routers import mission as mission_router
from api.routers import shop as shop_router
from api.routers import territory as territory_router
from api.routers import user as user_router
from api.routers import user_missions as user_missions_router
from core.config import settings
from core.database.db_helper import db_helper
from core.logging import setup_logging
from services.background_tasks import background_tasks_loop

# Configure logging from settings
setup_logging(level=settings.logging.level, fmt=settings.logging.fmt)

background_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global background_task
    background_task = asyncio.create_task(background_tasks_loop())
    yield
    # Shutdown
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass


import asyncio


app = FastAPI(
    title=settings.api.title,
    debug=settings.api.debug,
    root_path=settings.api.root_path,
    lifespan=lifespan,
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
app.include_router(shop_router.router)
app.include_router(dashboard_router.router)

# Serve Frontend Static Files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(FRONTEND_DIST_DIR):
    # Mount assets (css, js, images)
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST_DIR, "assets")),
        name="assets",
    )

    # Catch-all route to serve index.html for React Router
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST_DIR, "index.html"))


# Session dependency (routers use `api.dependencies.get_db`)
async def get_session() -> AsyncSession:
    async for session in db_helper.session_dependency():
        yield session
