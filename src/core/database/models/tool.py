from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .character import Character


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    bonus_intellect: Mapped[int] = mapped_column(default=0)
    bonus_agility: Mapped[int] = mapped_column(default=0)
    owner_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    owner: Mapped["Character"] = relationship(back_populates="tools")