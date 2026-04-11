from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from crud.other_crud import character_crud
from schemas.shop_item_schemas import ShopItemRead
from schemas.shop_schemas import ShopPurchaseRequest
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


@router.post("/buy")
async def buy_item(
    body: ShopPurchaseRequest,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Купить товар.
    Для оружия и инструментов нужно передать character_id.
    """
    service = ShopService(session)

    if body.character_id:
        # Проверяем, что персонаж принадлежит пользователю
        char = await character_crud.get(session, body.character_id)
        if not char or char.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Character not found or not yours"
            )

        result = await service.buy_item_for_character(
            current_user.id, body.item_id, body.character_id
        )
    else:
        result = await service.buy_item(current_user.id, body.item_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )
    return result
