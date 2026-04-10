"""Tests for mission stat types, reward calculations, and equipment requirements."""

from datetime import datetime, timedelta, timezone

import pytest

from core.database.models.enums import MissionStatType
from crud.other_crud import (
    character_crud,
    mission_crud,
    tool_crud,
    user_mission_crud,
    weapon_crud,
)
from services.mission_service import MissionService
from services.user_service import UserService


# ============================================================
# Reward calculation tests
# ============================================================


@pytest.mark.asyncio
async def test_force_mission_reward(db_session):
    """Force mission: reward based on total_power * 15."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7001, "force_tester")

    # Character with power=30 (main stat for force)
    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Brutus",
            "power": 30,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Armed Robbery",
            "description": "Rob a store",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "medium",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 2,
            "power_required": 20,
            "intellect_required": 5,
            "agility_required": 5,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    # medium: wanted=8, money=30*10=300
    assert res["rewards"]["reward_money"] == 300
    assert res["rewards"]["reward_influence"] == 10
    assert res["rewards"]["wanted_increase"] == 8

    # Complete and verify resources
    ums = await user_mission_crud.list(db_session)
    um = ums[0]
    um.ends_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.commit()

    complete_res = await svc.complete_mission(um.id)
    assert complete_res["success"] is True
    assert complete_res["reward_money"] == 300
    assert complete_res["reward_influence"] == 10
    assert complete_res["wanted_increase"] == 8


@pytest.mark.asyncio
async def test_stealth_mission_reward(db_session):
    """Stealth mission: reward based on total_agility * 15."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7002, "stealth_tester")

    # Character with agility=25 (main stat for stealth)
    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Shadow",
            "power": 5,
            "intellect": 10,
            "agility": 25,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Safe Cracking",
            "description": "Crack a safe",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "medium",
            "mission_stat_type": MissionStatType.STEALTH,
            "slots": 1,
            "power_required": 5,
            "intellect_required": 10,
            "agility_required": 20,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    # medium: wanted=8, money=25*10=250
    assert res["rewards"]["reward_money"] == 250
    assert res["rewards"]["reward_influence"] == 8
    assert res["rewards"]["wanted_increase"] == 8


@pytest.mark.asyncio
async def test_diplomacy_mission_reward(db_session):
    """Diplomacy mission: reward based on total_intellect * 15."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7003, "diplo_tester")

    # Character with intellect=40 (main stat for diplomacy)
    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "SilverTongue",
            "power": 5,
            "intellect": 40,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Cartel Deal",
            "description": "Negotiate with cartel",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "hard",
            "mission_stat_type": MissionStatType.DIPLOMACY,
            "slots": 1,
            "power_required": 5,
            "intellect_required": 30,
            "agility_required": 5,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    # hard: wanted=12, money=40*10=400
    assert res["rewards"]["reward_money"] == 400
    assert res["rewards"]["reward_influence"] == 13
    assert res["rewards"]["wanted_increase"] == 12


@pytest.mark.asyncio
async def test_reward_multiplier(db_session):
    """Flash mission with x2 reward multiplier."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7004, "flash_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Flash",
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
            "name": "Flash Hit",
            "description": "Quick job",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 15,
            "intellect_required": 0,
            "agility_required": 0,
            "reward_multiplier": 2.0,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    # easy: wanted=6, money=20*10*2=400
    assert res["rewards"]["reward_money"] == 400
    assert res["rewards"]["reward_influence"] == 12


# ============================================================
# Equipment requirement tests
# ============================================================


@pytest.mark.asyncio
async def test_mission_requires_weapon(db_session):
    """Mission with weapon_slots_required should fail without weapons."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7010, "weapon_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Unarmed",
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
            "name": "Armed Robbery",
            "description": "Needs a weapon",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 10,
            "intellect_required": 0,
            "agility_required": 0,
            "weapon_slots_required": 1,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is False
    assert "оружия" in res["message"].lower() or "weapon" in res["message"].lower()


@pytest.mark.asyncio
async def test_mission_with_weapon_passes(db_session):
    """Mission with weapon_slots_required should pass when character has weapon."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7011, "armed_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Armed",
            "power": 20,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    await weapon_crud.create(
        db_session,
        {
            "name": "Pistol",
            "bonus_power": 5,
            "owner_id": char.id,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Armed Robbery",
            "description": "Needs a weapon",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 10,
            "intellect_required": 0,
            "agility_required": 0,
            "weapon_slots_required": 1,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True


@pytest.mark.asyncio
async def test_mission_requires_tool(db_session):
    """Mission with tool_slots_required should fail without tools."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7012, "tool_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "NoTools",
            "power": 5,
            "intellect": 5,
            "agility": 20,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Safe Cracking",
            "description": "Needs tools",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.STEALTH,
            "slots": 1,
            "power_required": 0,
            "intellect_required": 5,
            "agility_required": 15,
            "tool_slots_required": 1,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is False
    assert "инструмент" in res["message"].lower() or "tool" in res["message"].lower()


@pytest.mark.asyncio
async def test_mission_with_tool_passes(db_session):
    """Mission with tool_slots_required should pass when character has tool."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7013, "tool_user")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "HasTools",
            "power": 5,
            "intellect": 5,
            "agility": 20,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    await tool_crud.create(
        db_session,
        {
            "name": "Lockpick",
            "bonus_intellect": 2,
            "bonus_agility": 3,
            "owner_id": char.id,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Safe Cracking",
            "description": "Needs tools",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.STEALTH,
            "slots": 1,
            "power_required": 0,
            "intellect_required": 5,
            "agility_required": 15,
            "tool_slots_required": 1,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True


# ============================================================
# Resource allocation tests
# ============================================================


@pytest.mark.asyncio
async def test_complete_mission_allocates_resources(db_session):
    """Completing a mission should add money, influence, and wanted level to user resources."""
    from crud.other_crud import user_resource_crud

    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7020, "resource_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Earner",
            "power": 25,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Money Job",
            "description": "Earn money",
            "duration": 1,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 15,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    ums = await user_mission_crud.list(db_session)
    um = ums[0]
    um.ends_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.commit()

    # Get resources before (refresh from DB)
    res_before = await user_resource_crud.get_by_user(db_session, user.id)
    money_before = res_before.money
    influence_before = res_before.influence
    wanted_before = res_before.wanted_level

    complete_res = await svc.complete_mission(um.id)
    assert complete_res["success"] is True

    # Refresh from DB after commit
    await db_session.commit()
    res_after = await user_resource_crud.get_by_user(db_session, user.id)
    assert res_after.money == money_before + complete_res["reward_money"]
    assert complete_res["wanted_increase"] == 6  # easy difficulty
    assert res_after.influence == influence_before + complete_res["reward_influence"]
    assert res_after.wanted_level == wanted_before + complete_res["wanted_increase"]


@pytest.mark.asyncio
async def test_failed_mission_no_reward(db_session):
    """Failed mission should not allocate resources."""
    from crud.other_crud import user_resource_crud

    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7021, "fail_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Unlucky",
            "power": 10,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Fail Mission",
            "description": "Will fail",
            "duration": 1,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    ums = await user_mission_crud.list(db_session)
    um = ums[0]
    um.ends_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.commit()

    res_before = await user_resource_crud.get_by_user(db_session, user.id)
    money_before = res_before.money
    influence_before = res_before.influence
    wanted_before = res_before.wanted_level

    # Manually set mission to FAILED to avoid randomness
    um.status = "failed"
    um.result = {
        "success": False,
        "events": [],
        "reward_money": 0,
        "reward_influence": 0,
        "wanted_increase": 0,
    }
    await db_session.commit()

    # Free character
    char.is_busy = False
    await db_session.commit()

    res_after = await user_resource_crud.get_by_user(db_session, user.id)
    assert res_after.money == money_before
    assert res_after.influence == influence_before
    assert res_after.wanted_level == wanted_before


# ============================================================
# is_mission_possible edge cases
# ============================================================


@pytest.mark.asyncio
async def test_mission_too_many_characters(db_session):
    """Should reject if more characters than mission slots."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7030, "multi_char")

    c1 = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "A",
            "power": 10,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )
    c2 = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "B",
            "power": 10,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Solo",
            "description": "Solo mission",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [c1, c2])
    assert res["success"] is False
    assert "много" in res["message"].lower() or "slots" in res["message"].lower()


@pytest.mark.asyncio
async def test_mission_busy_character(db_session):
    """Should reject if character is already busy."""
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(7031, "busy_tester")

    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Busy",
            "power": 10,
            "intellect": 5,
            "agility": 5,
            "loyalty": 0,
            "is_busy": True,
        },
    )

    mission = await mission_crud.create(
        db_session,
        {
            "name": "Test",
            "description": "test",
            "duration": 2,
            "reward_money": 0,
            "reward_influence": 0,
            "difficulty": "easy",
            "mission_stat_type": MissionStatType.FORCE,
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is False
    assert "занят" in res["message"].lower() or "busy" in res["message"].lower()
