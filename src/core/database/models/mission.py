from typing import TYPE_CHECKING

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user_mission import UserMission

class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))

    base_duration: Mapped[int] = mapped_column(Integer)  # seconds
    base_reward: Mapped[int] = mapped_column(Integer)
    base_risk: Mapped[int] = mapped_column(Integer)

    min_power_required: Mapped[int] = mapped_column(Integer)
    min_intellect_required: Mapped[int] = mapped_column(Integer)

    user_missions: Mapped[list["UserMission"]] = relationship(back_populates="mission")