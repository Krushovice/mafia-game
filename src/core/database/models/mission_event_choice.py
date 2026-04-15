"""Варианты выбора для событий миссий (облава, атака, удача)."""

from typing import TYPE_CHECKING

from sqlalchemy import Enum as PgEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .event import MissionEvent

from .enums import EventChoiceType


class MissionEventChoice(Base):
    """Вариант выбора для конкретного события."""

    __tablename__ = "mission_event_choices"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("mission_events.id"), index=True)
    choice_type: Mapped[EventChoiceType] = mapped_column(
        PgEnum(
            EventChoiceType,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(String(64), default="", server_default="")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")

    # Параметры для расчёта успеха
    money_cost: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    influence_required: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    power_required: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Базовый шанс успеха выбора (0-100)
    success_chance_base: Mapped[int] = mapped_column(
        Integer, default=50, server_default="50"
    )

    event: Mapped["MissionEvent"] = relationship(back_populates="choices")
