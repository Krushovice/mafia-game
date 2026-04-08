from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlalchemy import Enum as PgEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .mission import Mission

from .enums import MissionEventType


class MissionEvent(Base):
    __tablename__ = "mission_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"))
    event_type: Mapped[MissionEventType] = mapped_column(PgEnum(MissionEventType), nullable=False)
    chance: Mapped[int] = mapped_column(default=10, server_default="10")  # базовый шанс события в %
    description: Mapped[str] = mapped_column(default="", server_default="")  # текст описания события
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    mission: Mapped["Mission"] = relationship(back_populates="events")