"""Bot entry point for local development (polling mode).

For production, use FastAPI webhook mode instead.
"""

import asyncio
import os

from core.logging import setup_logging

from .config import settings
from .handlers import bot, dp


def main():
    """Run bot in polling mode for local development."""
    setup_logging(level="INFO")
    token = os.getenv("BOT_TELEGRAM_TOKEN") or getattr(settings, "telegram_token", None)
    if not token:
        raise RuntimeError(
            "Telegram bot token not set. Provide BOT_TELEGRAM_TOKEN env var or BOT_TELEGRAM_TOKEN in settings."
        )

    try:
        asyncio.run(dp.start_polling(bot))
    finally:
        asyncio.run(bot.session.close())


if __name__ == "__main__":
    main()
