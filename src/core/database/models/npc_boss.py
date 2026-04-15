"""NPCBoss model — NPC боссы, владеющие территориями."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .territory import Territory


class NPCBoss(Base):
    __tablename__ = "npc_bosses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    color: Mapped[str] = mapped_column(
        String(16), default="#ff4444"
    )  # hex color для карты

    influence: Mapped[int] = mapped_column(Integer, default=10)  # "размер" территории
    power: Mapped[int] = mapped_column(Integer, default=10)  # сложность захвата

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )

    # Связи
    territories: Mapped[list["Territory"]] = relationship(back_populates="boss")
