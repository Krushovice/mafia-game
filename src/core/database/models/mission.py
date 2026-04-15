from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .event import MissionEvent
    from .user_mission import UserMission

from .enums import MissionDifficulty, MissionStatType


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(128), nullable=False, default="", server_default=""
    )
    description: Mapped[str] = mapped_column(
        String(128), nullable=False, default="", server_default=""
    )
    duration: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )  # в секундах

    # Награды рассчитываются автоматически от главного стата, но можно переопределить
    reward_money: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    reward_influence: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    wanted_increase: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    difficulty: Mapped["MissionDifficulty"] = mapped_column(
        Enum(
            MissionDifficulty,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=MissionDifficulty.EASY,
        server_default="easy",
    )

    # Тип миссии определяет главный стат для расчёта награды
    mission_stat_type: Mapped["MissionStatType"] = mapped_column(
        Enum(
            MissionStatType,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        default=MissionStatType.FORCE,
        server_default="force",
    )

    slots: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    power_required: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    intellect_required: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    agility_required: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )

    # Требования к экипировке
    weapon_slots_required: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    tool_slots_required: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )

    # Множитель награды (flash = x1.5-2.0, territory = x1.0 но wanted x1.5)
    reward_multiplier: Mapped[float] = mapped_column(
        Float, default=1.0, server_default="1.0"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default="NOW()"
    )

    # Связи
    user_missions: Mapped[list["UserMission"]] = relationship(back_populates="mission")
    events: Mapped[list["MissionEvent"]] = relationship(back_populates="mission")
