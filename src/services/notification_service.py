"""Сервис очереди Telegram-уведомлений.

API/background-таски ставят сообщения в очередь через `enqueue_*`. Реальную
отправку делает диспетчер в боте (`src/bot/notification_dispatcher.py`),
поскольку API-контейнер не имеет сетевого доступа к api.telegram.org.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Notification
from core.database.models.enums import NotificationStatus, NotificationType

logger = logging.getLogger(__name__)


async def enqueue_notification(
    session: AsyncSession,
    user_id: int,
    notification_type: NotificationType,
    body: str,
    payload: dict[str, Any] | None = None,
    commit: bool = False,
) -> Notification:
    """Добавить уведомление в очередь. По умолчанию НЕ коммитит — вызывающий код
    отвечает за транзакцию."""
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        status=NotificationStatus.PENDING,
        body=body,
        payload=payload,
        attempts=0,
    )
    session.add(notification)
    await session.flush()
    if commit:
        await session.commit()
    return notification


def format_mission_completed(mission_name: str, result: dict) -> str:
    """HTML-сообщение об успешном завершении миссии."""
    money = result.get("reward_money", 0)
    influence = result.get("reward_influence", 0)
    wanted = result.get("wanted_increase", 0)

    lines = [f"✅ <b>Миссия завершена:</b> {_escape(mission_name)}"]
    if money:
        lines.append(f"💰 +{money} монет")
    if influence:
        lines.append(f"🌐 +{influence} влияния")
    if wanted:
        lines.append(f"⚠️ +{wanted} к розыску")
    return "\n".join(lines)


def format_mission_failed(mission_name: str) -> str:
    return f"❌ <b>Миссия провалена:</b> {_escape(mission_name)}"


def format_mission_event(mission_name: str, event_description: str) -> str:
    """HTML-сообщение об активном событии (облава) — игроку нужно открыть TMA и выбрать действие."""
    return (
        f"⚠️ <b>Событие во время миссии:</b> {_escape(mission_name)}\n\n"
        f"{_escape(event_description)}\n\n"
        "Открой приложение и выбери действие."
    )


def format_flash_mission(mission_name: str, expires_at_text: str) -> str:
    return (
        f"🔥 <b>Flash-миссия:</b> {_escape(mission_name)}\n"
        f"⏳ Доступна до {expires_at_text}\n"
        "Награда повышена!"
    )


def format_raid(description: str) -> str:
    return f"🚨 <b>Облава!</b>\n\n{_escape(description)}"


def _escape(text: str) -> str:
    """Экранирование для HTML parse_mode Telegram."""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
