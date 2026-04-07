from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user import User

class UserResource(Base):
    __tablename__ = "user_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    money: Mapped[int] = mapped_column(Integer, default=0)
    influence: Mapped[int] = mapped_column(Integer, default=0)
    wanted_level: Mapped[int] = mapped_column(Integer, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="resources")