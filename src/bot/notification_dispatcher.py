"""Notification dispatcher — забирает pending уведомления из БД и шлёт в Telegram.

Запускается в одном процессе с ботом (бот живёт вне Docker и имеет доступ к
api.telegram.org). API/background-таски пишут pending-записи через
`services.notification_service.enqueue_notification`.
"""

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models import Notification, User
from core.database.models.enums import NotificationStatus

logger = logging.getLogger(__name__)

# Интервал между опросами очереди, секунд
POLL_INTERVAL = 5

# Сколько pending-записей за один проход
BATCH_SIZE = 50

# После скольких попыток считаем уведомление окончательно проваленным
MAX_ATTEMPTS = 5


async def dispatch_pending_notifications(bot: Bot) -> None:
    """Один проход: забрать pending, отправить, обновить статусы."""
    try:
        async with AsyncSession(bind=db_helper.engine) as session:
            result = await session.execute(
                select(Notification, User.telegram_id)
                .join(User, User.id == Notification.user_id)
                .where(Notification.status == NotificationStatus.PENDING)
                .order_by(Notification.created_at.asc())
                .limit(BATCH_SIZE)
            )
            rows = result.all()

            if not rows:
                return

            logger.info(f"Dispatching {len(rows)} pending notifications")

            for notification, telegram_id in rows:
                await _send_one(session, bot, notification, telegram_id)

            await session.commit()

    except Exception:
        logger.exception("Error during notification dispatch")


async def _send_one(
    session: AsyncSession,
    bot: Bot,
    notification: Notification,
    telegram_id: int,
) -> None:
    """Отправить одно уведомление и обновить его статус."""
    notification.attempts += 1
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=notification.body,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except TelegramForbiddenError as e:
        # Пользователь заблокировал бота / не нажал /start — окончательно
        notification.status = NotificationStatus.FAILED
        notification.last_error = f"forbidden: {e}"
        logger.warning(
            f"Notification {notification.id} permanently failed (forbidden) for tg_id={telegram_id}"
        )
        return
    except TelegramRetryAfter as e:
        # Глобальный rate-limit Telegram — оставляем pending, ждём следующий проход
        notification.attempts -= 1  # не считаем попыткой
        notification.last_error = f"retry_after: {e.retry_after}s"
        logger.warning(f"Telegram rate limit, retry after {e.retry_after}s")
        # Ждать сразу — аккуратнее со всем тиком
        await asyncio.sleep(min(e.retry_after, 30))
        return
    except TelegramAPIError as e:
        notification.last_error = str(e)[:512]
        if notification.attempts >= MAX_ATTEMPTS:
            notification.status = NotificationStatus.FAILED
            logger.error(
                f"Notification {notification.id} failed after {MAX_ATTEMPTS} attempts: {e}"
            )
        else:
            logger.warning(
                f"Notification {notification.id} attempt {notification.attempts} failed: {e}"
            )
        return
    except Exception as e:
        notification.last_error = str(e)[:512]
        if notification.attempts >= MAX_ATTEMPTS:
            notification.status = NotificationStatus.FAILED
            logger.exception(
                f"Notification {notification.id} permanently failed after {MAX_ATTEMPTS} attempts"
            )
        return

    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.now(timezone.utc)
    notification.last_error = None


async def notification_dispatcher_loop(bot: Bot) -> None:
    """Бесконечный цикл диспетчера. Запускать как asyncio task рядом с polling."""
    logger.info("Starting notification dispatcher loop")
    while True:
        try:
            await dispatch_pending_notifications(bot)
        except Exception:
            logger.exception("Error in dispatcher iteration")
        await asyncio.sleep(POLL_INTERVAL)
