"""Тесты на services/notification_service: enqueue + форматтеры HTML-сообщений."""

import pytest
from sqlalchemy import select

from core.database.models import Notification
from core.database.models.enums import NotificationStatus, NotificationType
from services.notification_service import (
    _escape,
    enqueue_notification,
    format_flash_mission,
    format_mission_completed,
    format_mission_event,
    format_mission_failed,
    format_raid,
)
from services.user_service import UserService


@pytest.mark.asyncio
async def test_enqueue_notification_creates_pending_row(db_session):
    """enqueue_notification вставляет запись со статусом PENDING и attempts=0."""
    user = await UserService(db_session).get_or_create_by_telegram(7777, "notif_user")

    notif = await enqueue_notification(
        db_session,
        user_id=user.id,
        notification_type=NotificationType.MISSION_COMPLETED,
        body="hello",
        payload={"user_mission_id": 42},
    )
    await db_session.commit()

    fetched = (
        await db_session.execute(
            select(Notification).where(Notification.id == notif.id)
        )
    ).scalar_one()
    assert fetched.user_id == user.id
    assert fetched.notification_type == NotificationType.MISSION_COMPLETED
    assert fetched.status == NotificationStatus.PENDING
    assert fetched.body == "hello"
    assert fetched.payload == {"user_mission_id": 42}
    assert fetched.attempts == 0
    assert fetched.last_error is None
    assert fetched.sent_at is None


@pytest.mark.asyncio
async def test_enqueue_notification_with_commit_flag_persists(db_session):
    """commit=True должен закоммитить транзакцию сам."""
    user = await UserService(db_session).get_or_create_by_telegram(7778, "notif_user2")

    notif = await enqueue_notification(
        db_session,
        user_id=user.id,
        notification_type=NotificationType.GENERIC,
        body="x",
        commit=True,
    )

    fetched = (
        await db_session.execute(
            select(Notification).where(Notification.id == notif.id)
        )
    ).scalar_one()
    assert fetched.body == "x"


def test_format_mission_completed_full_payload():
    """Все награды присутствуют — все строки в выводе."""
    msg = format_mission_completed(
        "Грабёж банка",
        {"reward_money": 200, "reward_influence": 15, "wanted_increase": 5},
    )
    assert "✅" in msg
    assert "Грабёж банка" in msg
    assert "+200 монет" in msg
    assert "+15 влияния" in msg
    assert "+5 к розыску" in msg


def test_format_mission_completed_skips_zero_rewards():
    """Нулевые награды не должны появляться в сообщении."""
    msg = format_mission_completed(
        "Тихая миссия",
        {"reward_money": 0, "reward_influence": 0, "wanted_increase": 0},
    )
    assert "монет" not in msg
    assert "влияния" not in msg
    assert "розыску" not in msg
    assert "Тихая миссия" in msg


def test_format_mission_failed_contains_name():
    msg = format_mission_failed("Ограбление")
    assert "❌" in msg
    assert "Ограбление" in msg


def test_format_mission_event_contains_description():
    msg = format_mission_event("Налёт", "Копы у двери")
    assert "Налёт" in msg
    assert "Копы у двери" in msg
    assert "Открой приложение" in msg


def test_format_flash_mission_contains_expiry():
    msg = format_flash_mission("Срочное дело", "21:30")
    assert "🔥" in msg
    assert "Срочное дело" in msg
    assert "21:30" in msg


def test_format_raid():
    msg = format_raid("Облава на склад")
    assert "🚨" in msg
    assert "Облава на склад" in msg


def test_escape_handles_html_special_chars():
    """HTML-спецсимволы должны экранироваться, чтобы Telegram не падал на parse_mode=HTML."""
    assert _escape("a & b") == "a &amp; b"
    assert _escape("<script>") == "&lt;script&gt;"
    assert _escape("a < b > c & d") == "a &lt; b &gt; c &amp; d"


def test_escape_handles_none_safely():
    """Защита от None в имени/описании миссии."""
    assert _escape(None) == ""


def test_format_mission_completed_escapes_mission_name():
    """Имя миссии должно проходить через _escape."""
    msg = format_mission_completed(
        "<evil>", {"reward_money": 1, "reward_influence": 0, "wanted_increase": 0}
    )
    assert "<evil>" not in msg
    assert "&lt;evil&gt;" in msg
