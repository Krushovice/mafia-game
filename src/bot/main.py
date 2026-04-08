import asyncio
import logging
import os

from .config import settings
from .handlers import start_bot


def main():
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TELEGRAM_TOKEN") or getattr(settings, "telegram_token", None)
    if not token:
        raise RuntimeError("Telegram bot token not set. Provide BOT_TELEGRAM_TOKEN env var or BOT_TELEGRAM_TOKEN in settings.")
    asyncio.run(start_bot(token))


if __name__ == "__main__":
    main()
