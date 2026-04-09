from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, func, text
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
        Enum(MissionStatus, native_enum=False, length=32),
        default=MissionStatus.PENDING,
        server_default=text(f"'{MissionStatus.PENDING.value}'"),
    )

    started_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)

    success_chance: Mapped[int] = mapped_column(Integer)

    # Рассчитанные награды (сохраняются при старте миссии)
    reward_money: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=0, server_default="0"
    )
    reward_influence: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=0, server_default="0"
    )
    wanted_increase: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=0, server_default="0"
    )

    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )

    __table_args__ = (Index("ix_user_missions_ends_at_status", "ends_at", "status"),)

    user: Mapped["User"] = relationship(back_populates="missions")
    mission: Mapped["Mission"] = relationship(back_populates="user_missions")
    characters: Mapped[list["MissionCharacter"]] = relationship(
        back_populates="user_mission"
    )
