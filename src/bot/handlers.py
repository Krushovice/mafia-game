import logging
from typing import Optional

import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

from .config import settings

logger = logging.getLogger(__name__)


async def register_user_if_missing(
    client: httpx.AsyncClient, tg_id: int, username: Optional[str]
):
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

            # WebApp button requires HTTPS URL
            tma_url = settings.tma_url
            if tma_url.startswith("https://"):
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🎮 Играть",
                                web_app=WebAppInfo(url=tma_url),
                            )
                        ]
                    ]
                )
                await message.answer(
                    "Добро пожаловать в Мафию! Нажмите кнопку ниже, чтобы играть.",
                    reply_markup=keyboard,
                )
            else:
                await message.answer(
                    "Добро пожаловать в Мафию! 🎮\n\n"
                    "Игра доступна по командам:\n"
                    "/me — ваш профиль\n"
                    "/missions — список миссий\n"
                    "/my_missions — ваши активные миссии\n"
                    "/start_mission — запустить миссию\n"
                    "/complete_mission — завершить миссию\n\n"
                    "Для игры через Mini App нужен HTTPS URL."
                )

        @dp.message(Command(commands=["me"]))
        async def cmd_me(message: types.Message):
            tg_id = message.from_user.id
            try:
                r = await client.get(f"{settings.api_url}/users/{tg_id}")
                if r.status_code == 200:
                    await message.reply(f"Ваш профиль:\n{r.json()}")
                else:
                    await message.reply(
                        "Пользователь не найден. Отправьте /start."
                    )
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
                        lines.append(
                            f"{m.get('id')}: {m.get('title')} ({m.get('duration')}s)"
                        )
                    await message.reply("\n".join(lines))
                else:
                    await message.reply("Не удалось получить список миссий.")
            except Exception:
                logger.exception("Error fetching missions")
                await message.reply("Ошибка при запросе миссий.")

        @dp.message(Command(commands=["my_missions"]))
        async def cmd_my_missions(message: types.Message):
            tg_id = message.from_user.id
            headers = {
                "X-Telegram-Id": str(tg_id),
                "X-Username": message.from_user.username or "",
            }
            try:
                r = await client.get(
                    f"{settings.api_url}/user_missions",
                    headers=headers,
                )
                if r.status_code == 200:
                    ums = r.json()
                    if not ums:
                        await message.reply("У вас нет активных миссий.")
                        return
                    lines = []
                    for u in ums:
                        lines.append(
                            f"{u.get('id')}: mission={u.get('mission_id')} status={u.get('status')}"
                        )
                    await message.reply("\n".join(lines))
                else:
                    await message.reply("Не удалось получить ваши миссии.")
            except Exception:
                logger.exception("Error fetching user missions")
                await message.reply("Ошибка при запросе миссий.")

        @dp.message(Command(commands=["start_mission"]))
        async def cmd_start_mission(message: types.Message):
            # Usage: /start_mission <mission_id> <char_id1,char_id2,...>
            parts = (message.text or "").split()
            if len(parts) < 3:
                await message.reply(
                    "Использование: /start_mission <mission_id> <char_id1,char_id2,...>"
                )
                return
            try:
                mission_id = int(parts[1])
            except ValueError:
                await message.reply("mission_id должен быть числом")
                return
            rest = " ".join(parts[2:])
            try:
                char_ids = [int(x) for x in rest.replace(",", " ").split() if x]
            except ValueError:
                await message.reply(
                    "character ids должны быть числами, разделёнными запятыми или пробелами"
                )
                return
            headers = {
                "X-Telegram-Id": str(message.from_user.id),
                "X-Username": message.from_user.username or "",
            }
            payload = {"character_ids": char_ids}
            try:
                r = await client.post(
                    f"{settings.api_url}/missions/{mission_id}/start",
                    json=payload,
                    headers=headers,
                )
                if r.status_code in (200, 201):
                    await message.reply(f"Миссия запущена: {r.json()}")
                else:
                    await message.reply(
                        f"Не удалось запустить миссию: {r.status_code} {r.text}"
                    )
            except Exception:
                logger.exception("Error starting mission")
                await message.reply("Ошибка при запуске миссии.")

        @dp.message(Command(commands=["complete_mission"]))
        async def cmd_complete_mission(message: types.Message):
            # Usage: /complete_mission <user_mission_id>
            parts = (message.text or "").split()
            if len(parts) < 2:
                await message.reply(
                    "Использование: /complete_mission <user_mission_id>"
                )
                return
            try:
                um_id = int(parts[1])
            except ValueError:
                await message.reply("user_mission_id должен быть числом")
                return
            headers = {
                "X-Telegram-Id": str(message.from_user.id),
                "X-Username": message.from_user.username or "",
            }
            try:
                r = await client.post(
                    f"{settings.api_url}/user_missions/{um_id}/complete",
                    headers=headers,
                )
                if r.status_code == 200:
                    await message.reply(f"Миссия завершена: {r.json()}")
                else:
                    await message.reply(
                        f"Не удалось завершить миссию: {r.status_code} {r.text}"
                    )
            except Exception:
                logger.exception("Error completing mission")
                await message.reply("Ошибка при завершении миссии.")

        await dp.start_polling(bot)
