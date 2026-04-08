import pytest

from crud.other_crud import character_crud, weapon_crud, tool_crud, mission_crud


@pytest.mark.asyncio
async def test_create_and_list_weapons_tools(db_session):
    # create a user and character
    from services.user_service import UserService
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(5555, "equip_tester")

    char = await character_crud.create(db_session, {
        "user_id": user.id,
        "name": "EquipJoe",
        "power": 1,
        "intellect": 1,
        "agility": 1,
        "loyalty": 0,
        "is_busy": False,
    })

    w1 = await weapon_crud.create(db_session, {"name": "Knife", "bonus_power": 3, "owner_id": char.id})
    w2 = await weapon_crud.create(db_session, {"name": "Pistol", "bonus_power": 5, "owner_id": char.id})

    ws = await weapon_crud.list_by_owner(db_session, char.id)
    assert any(w.id == w1.id for w in ws)
    assert any(w.id == w2.id for w in ws)

    t1 = await tool_crud.create(db_session, {"name": "Lockpick", "bonus_intellect": 2, "bonus_agility": 0, "owner_id": char.id})
    ts = await tool_crud.list_by_owner(db_session, char.id)
    assert any(t.id == t1.id for t in ts)


@pytest.mark.asyncio
async def test_mission_and_character_list_helpers(db_session):
    # create mission and event-less listing
    m = await mission_crud.create(db_session, {"name": "ListTest", "description": "x", "duration": 10, "reward_money": 0, "reward_influence": 0, "difficulty": "easy", "slots": 1, "power_required": 0, "intellect_required": 0, "agility_required": 0})
    missions = await mission_crud.list_with_events(db_session)
    assert any(mi.id == m.id for mi in missions)

    # create user + character and list by user with equipment
    from services.user_service import UserService
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(6666, "list_helper")
    ch = await character_crud.create(db_session, {"user_id": user.id, "name": "Lister", "power": 1, "intellect": 1, "agility": 1, "loyalty": 0, "is_busy": False})
    # attach equipment
    await weapon_crud.create(db_session, {"name": "Fist", "bonus_power": 1, "owner_id": ch.id})
    chars = await character_crud.list_by_user_with_equipment(db_session, user.id)
    assert any(c.id == ch.id for c in chars)
