import logging
from typing import Optional

import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings

logger = logging.getLogger(__name__)


async def register_user_if_missing(client: httpx.AsyncClient, tg_id: int, username: Optional[str]):
    url = f"{settings.api_url}/users"
    payload = {"telegram_id": tg_id, "username": username or ""}
    try:
        r = await client.post(url, json=payload, timeout=10.0)
        if r.status_code in (200, 201):
            return r.json()
        else:
            logger.warning("Failed to register user %s: %s", tg_id, r.text)
    except Exception:
        logger.exception("Error while registering user")
    return None


async def start_bot(token: str):
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())

    async with httpx.AsyncClient() as client:

        @dp.message(Command(commands=["start"]))
        async def cmd_start(message: types.Message):
            user = message.from_user
            await register_user_if_missing(client, user.id, user.username)
            await message.reply("Добро пожаловать в Mafia Game! Я зарегистрировал вас.")

        @dp.message(Command(commands=["me"]))
        async def cmd_me(message: types.Message):
            tg_id = message.from_user.id
            try:
                r = await client.get(f"{settings.api_url}/users/{tg_id}")
                if r.status_code == 200:
                    await message.reply(f"Ваш профиль:\n{r.json()}")
                else:
                    await message.reply("Пользователь не найден. Отправьте /start.")
            except Exception:
                logger.exception("Error fetching user")
                await message.reply("Ошибка при запросе профиля.")

        @dp.message(Command(commands=["missions"]))
        async def cmd_missions(message: types.Message):
            try:
                r = await client.get(f"{settings.api_url}/missions")
                if r.status_code == 200:
                    missions = r.json()
                    if not missions:
                        await message.reply("Нет доступных миссий.")
                        return
                    lines = []
                    for m in missions:
                        lines.append(f"{m.get('id')}: {m.get('title')} ({m.get('duration')}s)")
                    await message.reply("\n".join(lines))
                else:
                    await message.reply("Не удалось получить список миссий.")
            except Exception:
                logger.exception("Error fetching missions")
                await message.reply("Ошибка при запросе миссий.")

        await dp.start_polling(bot)
