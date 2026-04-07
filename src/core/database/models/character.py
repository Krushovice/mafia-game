from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Integer, Boolean, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user import User
    from .mission_character import MissionCharacter
from .enums import CharacterRole, CharacterTrait


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(64))

    role: Mapped[CharacterRole] = mapped_column(
        Enum(
            CharacterRole,
            native_enum=False,
            length=32,
        )
    )
    trait: Mapped[CharacterTrait] = mapped_column(
        Enum(
            CharacterTrait,
            native_enum=False,
            length=32,
        )
    )

    power: Mapped[int] = mapped_column(Integer)
    agility: Mapped[int] = mapped_column(Integer)
    intellect: Mapped[int] = mapped_column(Integer)
    loyalty: Mapped[int] = mapped_column(Integer)


    is_busy: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="characters")
    mission_links: Mapped[list["MissionCharacter"]] = relationship(back_populates="character")
    # Связи с оружием и инструментами
    weapons: Mapped[list["Weapon"]] = relationship(back_populates="owner")
    tools: Mapped[list["Tool"]] = relationship(back_populates="owner")