from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .character import Character
    from .user_mission import UserMission


class MissionCharacter(Base):
    __tablename__ = "mission_characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_mission_id: Mapped[int] = mapped_column(
        ForeignKey("user_missions.id"), index=True
    )
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), index=True)
    slot_number: Mapped[int] = mapped_column(Integer)

    user_mission: Mapped["UserMission"] = relationship(back_populates="characters")
    character: Mapped["Character"] = relationship(back_populates="mission_links")
    __table_args__ = (
        # prevent same character being linked twice to same mission instance
        UniqueConstraint(
            "user_mission_id",
            "character_id",
            name="uq_mission_char_user_mission_character",
        ),
    )
