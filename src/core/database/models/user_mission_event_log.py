"""Лог событий в активной миссии пользователя."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .mission_event_choice import MissionEventChoice
    from .user_mission import UserMission

from .enums import EventChoiceType


class UserMissionEventLog(Base):
    """Запись о сработавшем событии в миссии пользователя.

    Хранит текущее активное событие, которое требует выбора игрока.
    """

    __tablename__ = "user_mission_event_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_mission_id: Mapped[int] = mapped_column(
        ForeignKey("user_missions.id"), index=True
    )
    event_choice_id: Mapped[int | None] = mapped_column(
        ForeignKey("mission_event_choices.id"), nullable=True
    )

    # Выбор игро (заполняется при respond_to_event)
    chosen_type: Mapped[EventChoiceType | None] = mapped_column(
        PgEnum(EventChoiceType, native_enum=False, length=32), nullable=True
    )

    resolved: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    result_description: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )

    user_mission: Mapped["UserMission"] = relationship(back_populates="event_logs")
    event_choice: Mapped["MissionEventChoice | None"] = relationship()
