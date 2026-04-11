"""Tests for starter package and wanted level blocking."""

import pytest

from core.database.models.enums import CharacterRole
from crud.other_crud import (
    character_crud,
    mission_crud,
    user_resource_crud,
)
from services.mission_service import MissionService
from services.user_service import UserService

# ============================================================
# Starter package tests
# ============================================================


@pytest.mark.asyncio
async def test_get_or_create_gives_starter_resources(db_session):
    """New user should получить 1000 coins, 10 influence, 0 wanted."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(8001, "starter_tester")

    resources = await user_resource_crud.get_by_user(db_session, user.id)
    assert resources is not None
    assert resources.money == 1000
    assert resources.influence == 10
    assert resources.wanted_level == 0


@pytest.mark.asyncio
async def test_get_or_create_gives_starter_character(db_session):
    """New user should получить 1 капо с универсальными статами."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(8002, "starter_char_tester")

    chars = await character_crud.list_by_user_with_equipment(db_session, user.id)
    assert len(chars) == 1

    capo = chars[0]
    assert capo.name == "Капо"
    assert capo.role == CharacterRole.CAPO
    assert capo.power == 10
    assert capo.intellect == 10
    assert capo.agility == 10
    assert capo.is_busy is False


@pytest.mark.asyncio
async def test_existing_user_doesnt_get_double_starter(db_session):
    """Повторный вызов get_or_create не должен дублировать ресурсы/персонажей."""
    svc = UserService(db_session)

    # First call — creates starter package
    user1 = await svc.get_or_create_by_telegram(8003, "no_double")

    # Second call — should return existing user
    user2 = await svc.get_or_create_by_telegram(8003, "no_double")
    assert user1.id == user2.id

    # Check no duplicate characters
    chars = await character_crud.list_by_user_with_equipment(db_session, user1.id)
    assert len(chars) == 1

    resources = await user_resource_crud.get_by_user(db_session, user1.id)
    assert resources.money == 1000


# ============================================================
# Wanted level blocking tests
# ============================================================


@pytest.mark.asyncio
async def test_mission_blocked_when_wanted_above_80(db_session):
    """При wanted > 80 нельзя начать миссию."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(8010, "wanted_tester")

    # Manually set wanted level above 80
    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.wanted_level = 85
    await db_session.commit()

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Criminal",
            "power": 20,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Easy Job",
            "description": "Simple",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    mission_svc = MissionService(db_session)
    res = await mission_svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is False
    assert "розыска" in res["message"].lower() or "розыск" in res["message"].lower()


@pytest.mark.asyncio
async def test_mission_allowed_when_wanted_below_80(db_session):
    """При wanted <= 80 можно начать миссию."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(8011, "low_wanted_tester")

    # Set wanted below threshold
    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.wanted_level = 75
    await db_session.commit()

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Clean",
            "power": 20,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Safe Job",
            "description": "Safe",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    mission_svc = MissionService(db_session)
    res = await mission_svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True


@pytest.mark.asyncio
async def test_mission_blocked_at_exactly_81(db_session):
    """wanted = 81 должен блокировать, wanted = 80 — нет."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(8012, "exact_81_tester")

    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.wanted_level = 81
    await db_session.commit()

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Hot",
            "power": 20,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Blocked",
            "description": "x",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    mission_svc = MissionService(db_session)
    res = await mission_svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is False
