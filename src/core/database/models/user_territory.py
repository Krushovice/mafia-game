"""UserTerritory model — связь пользователя с захваченной территорией."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .territory import Territory
    from .user import User


class UserTerritory(Base):
    __tablename__ = "user_territories"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    territory_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"), index=True
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )

    # Связи
    user: Mapped["User"] = relationship(back_populates="territories")
    territory: Mapped["Territory"] = relationship(
        back_populates="user_territories"
    )
