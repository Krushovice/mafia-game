from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from schemas.shop_item_schemas import ShopItemRead
from services.shop_service import ShopService

router = APIRouter(prefix="/shop", tags=["Shop"])


@router.get(
    "/",
    response_model=list[ShopItemRead],
)
async def list_shop_items(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Список доступных товаров в магазине."""
    service = ShopService(session)
    return await service.list_available()


@router.post("/buy/{item_id}")
async def buy_item(
    item_id: int,
    character_id: int | None = None,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Купить товар. Для оружия и инструментов нужен character_id."""
    service = ShopService(session)
    result = await service.buy_item(current_user.id, item_id)

    # Если нужно выбрать персонажа (оружие/инструмент)
    if character_id and result.get("message") and (
        "character_id" in result.get("message", "")
    ):
        result = await service.buy_weapon_for_character(
            current_user.id, item_id, character_id
        )
        # Пробуем купить как инструмент если не оружие
        if not result.get("success"):
            result = await service.buy_tool_for_character(
                current_user.id, item_id, character_id
            )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result
