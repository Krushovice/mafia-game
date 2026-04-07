from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user_mission import UserMission
    from .character import Character

class MissionCharacter(Base):
    __tablename__ = "mission_characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_mission_id: Mapped[int] = mapped_column(
        ForeignKey("user_missions.id"), index=True
    )
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"), index=True
    )

    user_mission: Mapped["UserMission"] = relationship(back_populates="characters")
    character: Mapped["Character"] = relationship(back_populates="mission_links")