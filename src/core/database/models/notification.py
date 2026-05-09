"""Notification — очередь Telegram-уведомлений.

API/background-таски пишут pending-записи. Бот периодически читает очередь,
шлёт сообщения через aiogram и помечает sent/failed. Архитектура нужна потому,
что API-контейнер не имеет сетевого доступа к api.telegram.org.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import NotificationStatus, NotificationType

if TYPE_CHECKING:
    from .user import User


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(
            NotificationType,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )

    status: Mapped[NotificationStatus] = mapped_column(
        Enum(
            NotificationStatus,
            native_enum=True,
            values_callable=lambda e: [i.value for i in e],
        ),
        default=NotificationStatus.PENDING,
        server_default=text(f"'{NotificationStatus.PENDING.value}'"),
        nullable=False,
        index=True,
    )

    # Готовый текст сообщения (HTML-форматирование)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Произвольные данные (id миссии, награды и т.п.) — для отладки и для будущих кнопок
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Счётчик попыток отправки
    attempts: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    last_error: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_notifications_status_created_at", "status", "created_at"),
    )
