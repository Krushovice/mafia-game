from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Integer, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user_mission import UserMission
    from .event import MissionEvent
from .enums import MissionDifficulty



class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False, default="", server_default="")
    description: Mapped[str] = mapped_column(String(128), nullable=False, default="", server_default="")
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")  # в секундах

    reward_money: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    reward_influence: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    difficulty: Mapped["MissionDifficulty"] = mapped_column(
        Enum("MissionDifficulty", native_enum=False, length=32),
        nullable=False,
        default="easy",
        server_default="easy"
    )

    slots: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    power_required: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    intellect_required: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    agility_required: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, server_default="NOW()")

    # Связи
    user_missions: Mapped[list["UserMission"]] = relationship(back_populates="mission")
    events: Mapped[list["MissionEvent"]] = relationship(back_populates="mission")