from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Integer, Enum, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user import User
    from .mission import Mission
    from .mission_character import MissionCharacter

from .enums import MissionStatus


class UserMission(Base):
    __tablename__ = "user_missions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"))

    status: Mapped[MissionStatus] = mapped_column(
        Enum(
            MissionStatus,
            native_enum=False,
            length=32
        ),
        default=MissionStatus.PENDING,
        server_default=text(f"'{MissionStatus.PENDING.value}'"),
    )

    started_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)

    success_chance: Mapped[int] = mapped_column(Integer)
    result_reward: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="missions")
    mission: Mapped["Mission"] = relationship(back_populates="user_missions")
    characters: Mapped[list["MissionCharacter"]] = relationship(back_populates="user_mission")