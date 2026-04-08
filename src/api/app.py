from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from crud.other_crud import CRUDCharacter, CRUDMission
from services.mission_service import MissionService

app = FastAPI()

character_crud = CRUDCharacter
mission_crud = CRUDMission

# ---------------------------------------------------
# 🔹 Сессия зависимость
# ---------------------------------------------------
async def get_session() -> AsyncSession:
    async for session in db_helper.session_dependency():
        yield session

# ---------------------------------------------------
# 🔹 Список миссий
# ---------------------------------------------------
@app.get("/missions")
async def get_missions(session: AsyncSession = Depends(get_session)):
    missions = await mission_crud.list(session)
    return missions

# ---------------------------------------------------
# 🔹 Список персонажей
# ---------------------------------------------------
@app.get("/characters")
async def get_characters(session: AsyncSession = Depends(get_session)):
    characters = await character_crud.list_with_equipment(session=session)
    return characters

# ---------------------------------------------------
# 🔹 Запуск миссии
# ---------------------------------------------------
@app.post("/missions/{mission_id}/run")
async def run_mission(mission_id: int, character_ids: list[int], session: AsyncSession = Depends(get_session)):
    characters = []
    for cid in character_ids:
        c = await character_crud.get(session, cid)
        if not c:
            raise HTTPException(status_code=404, detail=f"Character {cid} not found")
        characters.append(c)

    result = await MissionService.run_mission(session, mission_id, characters)
    return result

# ---------------------------------------------------
# 🔹 Добавление персонажа (для теста)
# ---------------------------------------------------
@app.post("/characters/add")
async def add_character(name: str, power: int, intellect: int, agility: int, session: AsyncSession = Depends(get_session)):
    char = await character_crud.create(session, {"name": name, "power": power, "intellect": intellect, "agility": agility})
    return char