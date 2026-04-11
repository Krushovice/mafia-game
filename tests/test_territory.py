"""Tests for territory system."""

import pytest

from core.database.models.enums import TerritoryType
from crud.other_crud import (
    character_crud,
    territory_crud,
    user_resource_crud,
    user_territory_crud,
)
from services.territory_service import TerritoryService
from services.user_service import UserService


async def _seed_territories(db_session):
    """Seed territories for tests."""
    existing = await territory_crud.list(db_session)
    if existing:
        return
    territories_data = [
        {
            "name": "Test District 1",
            "territory_type": TerritoryType.DISTRICT,
            "description": "First territory",
            "influence_required": 25,
            "power_required": 20,
            "intellect_required": 15,
            "agility_required": 15,
            "reward_influence": 15,
            "reward_money": 200,
            "passive_income_money": 50,
            "passive_income_influence": 1,
            "display_order": 1,
        },
        {
            "name": "Test District 2",
            "territory_type": TerritoryType.DISTRICT,
            "description": "Second territory",
            "influence_required": 40,
            "power_required": 25,
            "intellect_required": 20,
            "agility_required": 20,
            "reward_influence": 15,
            "reward_money": 300,
            "passive_income_money": 75,
            "passive_income_influence": 1,
            "display_order": 2,
        },
    ]
    for data in territories_data:
        await territory_crud.create(db_session, data)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_territories(db_session):
    """List territories ordered by display_order."""
    await _seed_territories(db_session)
    territories = await territory_crud.list_ordered(db_session)
    assert len(territories) == 2
    assert territories[0].display_order < territories[1].display_order


@pytest.mark.asyncio
async def test_list_for_user_shows_available(db_session):
    """User with low influence should see locked territories."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9001, "territory_tester")

    territory_svc = TerritoryService(db_session)
    await _seed_territories(db_session)
    result = await territory_svc.list_for_user(user.id, 10)  # low influence

    assert len(result) == 2
    # First territory requires 25 influence, user has 10 → can't attempt
    assert result[0]["is_captured"] is False
    assert result[0]["can_attempt"] is False


@pytest.mark.asyncio
async def test_list_for_user_shows_capturable(db_session):
    """User with enough influence should see capturable territory."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9002, "high_influence_tester")

    # Give user enough influence
    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.influence = 30
    await db_session.commit()

    territory_svc = TerritoryService(db_session)
    await _seed_territories(db_session)
    result = await territory_svc.list_for_user(user.id, 30)

    # First territory requires 25 influence, user has 30 → can attempt
    assert result[0]["can_attempt"] is True


@pytest.mark.asyncio
async def test_start_capture_requires_3_characters(db_session):
    """Territory capture requires exactly 3 characters."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9010, "capture_tester")

    # Create only 2 characters
    c1 = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "A",
            "power": 30,
            "intellect": 20,
            "agility": 20,
            "loyalty": 0,
            "is_busy": False,
        },
    )
    c2 = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "B",
            "power": 30,
            "intellect": 20,
            "agility": 20,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    await _seed_territories(db_session)
    territories = await territory_crud.list_ordered(db_session)
    territory_svc = TerritoryService(db_session)

    res = await territory_svc.start_capture(user.id, territories[0].id, [c1.id, c2.id])
    assert res["success"] is False
    assert "влияния" in res["message"].lower() or "3" in res["message"]


@pytest.mark.asyncio
async def test_start_capture_fails_without_enough_influence(db_session):
    """Can't start capture without enough influence."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9011, "low_influence_capture")

    # Create 3 characters
    chars = []
    for i in range(3):
        c = await character_crud.create(
            db_session,
            {
                "user_id": user.id,
                "name": f"Cap{i}",
                "power": 30,
                "intellect": 20,
                "agility": 20,
                "loyalty": 0,
                "is_busy": False,
            },
        )
        chars.append(c)

    await _seed_territories(db_session)
    territories = await territory_crud.list_ordered(db_session)
    territory_svc = TerritoryService(db_session)

    # User has only 10 influence, territory requires 25
    res = await territory_svc.start_capture(
        user.id, territories[0].id, [c.id for c in chars]
    )
    assert res["success"] is False
    assert "влияния" in res["message"].lower()


@pytest.mark.asyncio
async def test_capture_marks_characters_busy(db_session):
    """Characters should be marked busy after starting capture."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9012, "busy_capture")

    chars = []
    for i in range(3):
        c = await character_crud.create(
            db_session,
            {
                "user_id": user.id,
                "name": f"Busy{i}",
                "power": 30,
                "intellect": 20,
                "agility": 20,
                "loyalty": 0,
                "is_busy": False,
            },
        )
        chars.append(c)

    # Give user enough influence
    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.influence = 30
    await db_session.commit()

    await _seed_territories(db_session)
    territories = await territory_crud.list_ordered(db_session)
    territory_svc = TerritoryService(db_session)

    res = await territory_svc.start_capture(
        user.id, territories[0].id, [c.id for c in chars]
    )
    assert res["success"] is True

    # Check characters are busy
    for c in chars:
        refreshed = await character_crud.get(db_session, c.id)
        assert refreshed.is_busy is True


@pytest.mark.asyncio
async def test_passive_income_calculation(db_session):
    """Calculate passive income from captured territories."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9020, "income_tester")

    # Capture first territory (50 coins, 1 influence per tick)
    await _seed_territories(db_session)
    territories = await territory_crud.list_ordered(db_session)

    await user_territory_crud.create(
        db_session,
        {
            "user_id": user.id,
            "territory_id": territories[0].id,
        },
    )
    await db_session.commit()

    income = await user_territory_crud.get_total_passive_income(db_session, user.id)
    assert income["money"] == 50
    assert income["influence"] == 1


@pytest.mark.asyncio
async def test_already_captured_territory(db_session):
    """Can't capture territory twice."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9021, "double_capture")

    chars = []
    for i in range(3):
        c = await character_crud.create(
            db_session,
            {
                "user_id": user.id,
                "name": f"DC{i}",
                "power": 30,
                "intellect": 20,
                "agility": 20,
                "loyalty": 0,
                "is_busy": False,
            },
        )
        chars.append(c)

    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.influence = 30
    await db_session.commit()

    await _seed_territories(db_session)
    territories = await territory_crud.list_ordered(db_session)
    territory_svc = TerritoryService(db_session)

    # First capture
    res1 = await territory_svc.start_capture(
        user.id, territories[0].id, [c.id for c in chars]
    )
    assert res1["success"] is True
