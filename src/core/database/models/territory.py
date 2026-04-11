"""Territory model — территории для захвата."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_territory import UserTerritory

from .enums import TerritoryType


class Territory(Base):
    __tablename__ = "territories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    territory_type: Mapped[TerritoryType] = mapped_column(
        Enum(TerritoryType, native_enum=False, length=32),
        nullable=False,
        default=TerritoryType.DISTRICT,
    )

    description: Mapped[str] = mapped_column(
        String(256), default="", server_default=""
    )

    # Требования для миссии захвата
    influence_required: Mapped[int] = mapped_column(Integer, default=25)
    power_required: Mapped[int] = mapped_column(Integer, default=20)
    intellect_required: Mapped[int] = mapped_column(Integer, default=15)
    agility_required: Mapped[int] = mapped_column(Integer, default=15)

    # Награда за захват
    reward_influence: Mapped[int] = mapped_column(Integer, default=15)
    reward_money: Mapped[int] = mapped_column(Integer, default=200)

    # Пассивный доход за тик (10 минут)
    passive_income_money: Mapped[int] = mapped_column(Integer, default=50)
    passive_income_influence: Mapped[int] = mapped_column(Integer, default=1)

    # Порядок отображения
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )

    # Связи
    user_territories: Mapped[list["UserTerritory"]] = relationship(
        back_populates="territory"
    )
