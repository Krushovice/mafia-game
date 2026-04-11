from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from crud.other_crud import tool_crud, weapon_crud
from schemas import ToolRead, WeaponRead
from schemas.weapon_tool_schemas import ToolCreate, WeaponCreate

router = APIRouter(prefix="/equipment", tags=["Equipment"])


@router.post(
    "/weapons/",
    response_model=WeaponRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_weapon(
    data: WeaponCreate,
    session: AsyncSession = Depends(get_db),
):
    payload = data.model_dump()
    weapon = await weapon_crud.create(session, payload)
    return weapon


@router.get(
    "/weapons/owner/{owner_id}",
    response_model=list[WeaponRead],
)
async def list_weapons_by_owner(
    owner_id: int,
    session: AsyncSession = Depends(get_db),
):
    weapons = await weapon_crud.list_by_owner(session, owner_id)
    return weapons


@router.delete("/weapons/{weapon_id}")
async def delete_weapon(
    weapon_id: int,
    session: AsyncSession = Depends(get_db),
):
    deleted = await weapon_crud.delete(session, weapon_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Weapon not found",
        )
    return {"success": True}


@router.post(
    "/tools/",
    response_model=ToolRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_tool(
    data: ToolCreate,
    session: AsyncSession = Depends(get_db),
):
    payload = data.model_dump()
    tool = await tool_crud.create(session, payload)
    return tool


@router.get(
    "/tools/owner/{owner_id}",
    response_model=list[ToolRead],
)
async def list_tools_by_owner(
    owner_id: int,
    session: AsyncSession = Depends(get_db),
):
    tools = await tool_crud.list_by_owner(session, owner_id)
    return tools


@router.delete("/tools/{tool_id}")
async def delete_tool(
    tool_id: int,
    session: AsyncSession = Depends(get_db),
):
    deleted = await tool_crud.delete(session, tool_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tool not found",
        )
    return {"success": True}
