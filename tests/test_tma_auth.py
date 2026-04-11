"""Tests for Telegram WebApp initData validation."""

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from api.tma_auth import validate_init_data


def _make_init_data(user_data: dict, bot_token: str) -> str:
    """Generate a valid initData string for testing."""
    user_json = json.dumps(user_data, separators=(",", ":"))
    data = {"user": user_json, "auth_date": str(int(time.time()))}

    # Build data_check_string
    data_check_arr = sorted(data.items())
    data_check_string = "\n".join(f"{k}={v}" for k, v in data_check_arr)

    # HMAC-SHA256
    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    hash_val = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    data["hash"] = hash_val
    return urlencode(data)


class TestValidateInitData:
    BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

    def test_valid_init_data(self):
        """Valid initData should return user data."""
        user_data = {
            "id": 12345,
            "first_name": "Test",
            "username": "testuser",
        }
        init_data = _make_init_data(user_data, self.BOT_TOKEN)

        result = validate_init_data(init_data, self.BOT_TOKEN)
        assert result["id"] == 12345
        assert result["first_name"] == "Test"
        assert result["username"] == "testuser"

    def test_empty_init_data_raises(self):
        """Empty initData should raise 401."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            validate_init_data("", self.BOT_TOKEN)
        assert exc.value.status_code == 401

    def test_missing_hash_raises(self):
        """initData without hash should raise 401."""
        from fastapi import HTTPException

        user_data = {"id": 12345, "first_name": "Test"}
        data = {
            "user": json.dumps(user_data),
            "auth_date": str(int(time.time())),
        }

        with pytest.raises(HTTPException) as exc:
            validate_init_data(urlencode(data), self.BOT_TOKEN)
        assert exc.value.status_code == 401

    def test_invalid_hash_raises(self):
        """initData with wrong hash should raise 401."""
        from fastapi import HTTPException

        user_data = {"id": 12345, "first_name": "Test"}
        data = {
            "user": json.dumps(user_data),
            "auth_date": str(int(time.time())),
            "hash": "invalid_hash_12345",
        }

        with pytest.raises(HTTPException) as exc:
            validate_init_data(urlencode(data), self.BOT_TOKEN)
        assert exc.value.status_code == 401

    def test_wrong_bot_token_raises(self):
        """initData validated with wrong bot token should raise 401."""
        from fastapi import HTTPException

        user_data = {"id": 12345, "first_name": "Test"}
        init_data = _make_init_data(user_data, self.BOT_TOKEN)

        with pytest.raises(HTTPException) as exc:
            validate_init_data(init_data, "wrong_token_123")
        assert exc.value.status_code == 401

    def test_invalid_user_json_raises(self):
        """initData with invalid user JSON should raise 401."""
        from fastapi import HTTPException

        data = {
            "user": "{invalid json}",
            "auth_date": str(int(time.time())),
        }

        # We need a valid hash for this test, but the JSON is invalid
        # The hash won't match anyway, but let's test the flow
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(data.items())
        )
        secret_key = hashlib.sha256(self.BOT_TOKEN.encode("utf-8")).digest()
        hash_val = hmac.new(
            secret_key,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        data["hash"] = hash_val

        with pytest.raises(HTTPException) as exc:
            validate_init_data(urlencode(data), self.BOT_TOKEN)
        assert exc.value.status_code == 401

    def test_missing_user_id_raises(self):
        """initData without user id should raise 401 from dependency level,
        but validate_init_data itself should still return the dict."""
        user_data = {"first_name": "NoId"}
        init_data = _make_init_data(user_data, self.BOT_TOKEN)

        result = validate_init_data(init_data, self.BOT_TOKEN)
        assert "id" not in result or result.get("id") is None
