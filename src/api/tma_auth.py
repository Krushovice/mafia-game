"""Telegram Mini App (TMA) authentication utilities.

Validates `initData` sent by Telegram WebApp SDK and extracts user information.
See: https://core.telegram.org/bots/webapps#validating-init-data
"""

import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qs

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def validate_init_data(init_data: str, bot_token: str) -> dict:
    """Validate Telegram WebApp initData and return parsed user data.

    Args:
        init_data: Raw initData string from Telegram WebApp (tg.initData).
        bot_token: Telegram bot token (same as used for the bot).

    Returns:
        Parsed user data dict with keys: id, first_name, username, etc.

    Raises:
        HTTPException 401 if initData is invalid or expired.
    """
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="initData is empty",
        )

    parsed = parse_qs(init_data)
    received_hash = parsed.get("hash", [""])[0]

    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="initData has no hash",
        )

    # Build data_check_string: sorted key=value pairs joined by \n, excluding "hash"
    data_check_arr = sorted([(k, v[0]) for k, v in parsed.items() if k != "hash"])
    data_check_string = "\n".join(f"{k}={v}" for k, v in data_check_arr)

    # HMAC-SHA256: secret_key = SHA256(bot_token)
    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        logger.warning(
            "Invalid initData hash: received=%s, computed=%s",
            received_hash,
            computed_hash,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid initData signature",
        )

    # Extract user data
    user_data_raw = parsed.get("user", ["{}"])[0]
    try:
        user_data = json.loads(user_data_raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user data in initData",
        )

    return user_data
