"""ShopItem model — товары магазина (бойцы, оружие, инструменты)."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User

from .enums import CharacterRole, CharacterTrait, ShopItemType


class ShopItem(Base):
    __tablename__ = "shop_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    description: Mapped[str] = mapped_column(String(256), nullable=False, default="")

    item_type: Mapped[ShopItemType] = mapped_column(
        Enum(
            ShopItemType,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=ShopItemType.CHARACTER,
    )

    # Цена
    cost_money: Mapped[int] = mapped_column(Integer, default=0)
    cost_influence: Mapped[int] = mapped_column(Integer, default=0)

    # Для персонажей
    role: Mapped[CharacterRole | None] = mapped_column(
        Enum(
            CharacterRole,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=True,
    )
    trait: Mapped[CharacterTrait | None] = mapped_column(
        Enum(
            CharacterTrait,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=True,
    )
    base_power: Mapped[int] = mapped_column(Integer, default=0)
    base_intellect: Mapped[int] = mapped_column(Integer, default=0)
    base_agility: Mapped[int] = mapped_column(Integer, default=0)
    base_loyalty: Mapped[int] = mapped_column(Integer, default=0)

    # Для оружия и инструментов
    bonus_power: Mapped[int] = mapped_column(Integer, default=0)
    bonus_intellect: Mapped[int] = mapped_column(Integer, default=0)
    bonus_agility: Mapped[int] = mapped_column(Integer, default=0)

    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )

    display_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )

    # Кто купил
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    buyer: Mapped["User | None"] = relationship(back_populates="shop_purchases")
