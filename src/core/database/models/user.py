from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .character import Character
    from .shop_item import ShopItem
    from .user_mission import UserMission
    from .user_resource import UserResource
    from .user_territory import UserTerritory


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now(),
    )

    # relationships
    resources: Mapped["UserResource"] = relationship(
        back_populates="user", uselist=False
    )
    characters: Mapped[list["Character"]] = relationship(back_populates="user")
    missions: Mapped[list["UserMission"]] = relationship(back_populates="user")
    territories: Mapped[list["UserTerritory"]] = relationship(back_populates="user")
    shop_purchases: Mapped[list["ShopItem"]] = relationship(
        back_populates="buyer",
    )
