from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum as PgEnum
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

    mission: Mapped["Mission"] = relationship(back_populates="events")