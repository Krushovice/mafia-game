from datetime import datetime
from sqlalchemy import ForeignKey, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    type: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(255))

    processed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now()
    )