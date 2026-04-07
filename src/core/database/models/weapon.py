from typing import TYPE_CHECKING

from sqlalchemy import  ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .character import Character


class Weapon(Base):
    __tablename__ = "weapons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    bonus_power: Mapped[int]  # сколько добавляет к силе персонажа
    owner_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    owner: Mapped["Character"] = relationship(back_populates="weapons")