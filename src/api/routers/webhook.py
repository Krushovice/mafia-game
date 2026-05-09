"""Telegram Webhook Router.

Receives updates from Telegram and processes them through aiogram dispatcher.
"""

import logging

from aiogram.types import Update
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from bot.config import settings as bot_settings
from bot.handlers import bot, dp

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Telegram Webhook"])


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming updates from Telegram."""
    # Parse update from request body
    update_data = await request.json()
    update = Update.model_validate(update_data, context={"bot": bot})

    # Process update through dispatcher
    try:
        await dp.feed_update(bot, update)
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.exception("Error processing webhook update")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
        )


@router.get("/webhook/info")
async def webhook_info():
    """Get current webhook status from Telegram."""
    try:
        info = await bot.get_webhook_info()
        return {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections,
            "ip_address": info.ip_address,
        }
    except Exception as e:
        logger.exception("Error getting webhook info")
        return {"error": str(e)}


@router.post("/webhook/set")
async def set_webhook(url: str | None = None):
    """Manually set webhook URL."""
    webhook_url = url or bot_settings.webhook_url
    if not webhook_url:
        return {"error": "webhook_url not configured"}

    try:
        await bot.set_webhook(webhook_url)
        return {"status": "ok", "url": webhook_url}
    except Exception as e:
        logger.exception("Error setting webhook")
        return {"error": str(e)}


@router.post("/webhook/delete")
async def delete_webhook():
    """Delete webhook (switch to polling mode)."""
    try:
        await bot.delete_webhook()
        return {"status": "ok", "message": "Webhook deleted"}
    except Exception as e:
        logger.exception("Error deleting webhook")
        return {"error": str(e)}
