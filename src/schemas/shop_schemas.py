"""Schemas for shop operations."""

from pydantic import BaseModel


class ShopPurchaseRequest(BaseModel):
    """Request body for purchasing an item."""

    item_id: int
    character_id: int | None = None
