"""Bot entry point for local development (polling mode).

For production, use FastAPI webhook mode instead.
"""

import asyncio
import logging
import os

from core.logging import setup_logging

from .config import settings
from .handlers import bot, dp
from .notification_dispatcher import notification_dispatcher_loop

logger = logging.getLogger(__name__)


async def _run() -> None:
    """Запускает polling и notification dispatcher параллельно."""
    polling_task = asyncio.create_task(dp.start_polling(bot), name="bot_polling")
    dispatcher_task = asyncio.create_task(
        notification_dispatcher_loop(bot), name="notification_dispatcher"
    )

    done, pending = await asyncio.wait(
        {polling_task, dispatcher_task},
        return_when=asyncio.FIRST_EXCEPTION,
    )

    for task in pending:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass

    for task in done:
        if task.exception():
            logger.exception("Task %s crashed: %s", task.get_name(), task.exception())


def main():
    """Run bot in polling mode for local development."""
    setup_logging(level="INFO")
    token = os.getenv("BOT_TELEGRAM_TOKEN") or getattr(settings, "telegram_token", None)
    if not token:
        raise RuntimeError(
            "Telegram bot token not set. Provide BOT_TELEGRAM_TOKEN env var or BOT_TELEGRAM_TOKEN in settings."
        )

    try:
        asyncio.run(_run())
    finally:
        asyncio.run(bot.session.close())


if __name__ == "__main__":
    main()
