"""Tests for shop system."""

import pytest

from core.database.models.enums import ShopItemType
from crud.other_crud import (
    character_crud,
    shop_item_crud,
    user_resource_crud,
)
from services.shop_service import ShopService
from services.user_service import UserService


@pytest.mark.asyncio
async def test_list_available_shop_items(db_session):
    """List should return all available items."""
    await _seed_shop(db_session)
    service = ShopService(db_session)
    items = await service.list_available()
    assert len(items) == 3
    assert any(i["item_type"] == "character" for i in items)
    assert any(i["item_type"] == "weapon" for i in items)
    assert any(i["item_type"] == "tool" for i in items)


@pytest.mark.asyncio
async def test_buy_character_success(db_session):
    """Buy a character — should deduct money and create character."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9100, "shop_buyer")

    # Find the "Боевик" character item
    await _seed_shop(db_session)
    shop_svc = ShopService(db_session)
    items = await shop_svc.list_available()
    fighter = next(i for i in items if i["item_type"] == "character")

    result = await shop_svc.buy_item(user.id, fighter["id"])
    assert result["success"] is True
    assert "Куплен боец" in result["message"]

    # Check money was deducted
    resources = await user_resource_crud.get_by_user(db_session, user.id)
    assert resources.money == 1000 - fighter["cost_money"]


@pytest.mark.asyncio
async def test_buy_character_not_enough_money(db_session):
    """Should fail if user doesn't have enough money."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9101, "poor_buyer")

    # Reduce user's money
    resources = await user_resource_crud.get_by_user(db_session, user.id)
    resources.money = 100
    await db_session.commit()

    await _seed_shop(db_session)
    shop_svc = ShopService(db_session)
    items = await shop_svc.list_available()
    expensive = next(
        i
        for i in items
        if i["item_type"] == "character" and i["cost_money"] > 100
    )

    result = await shop_svc.buy_item(user.id, expensive["id"])
    assert result["success"] is False
    assert "Нужно" in result["message"]


@pytest.mark.asyncio
async def test_buy_weapon_for_character(db_session):
    """Buy weapon for a specific character."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9102, "weapon_buyer")

    # Create a character to own the weapon
    capo = await character_crud.create(db_session, {
        "user_id": user.id,
        "name": "BuyerCapo",
        "power": 10,
        "intellect": 10,
        "agility": 10,
        "loyalty": 10,
        "is_busy": False,
    })

    await _seed_shop(db_session)
    shop_svc = ShopService(db_session)
    items = await shop_svc.list_available()
    knife = next(i for i in items if i["item_type"] == "weapon")

    result = await shop_svc.buy_weapon_for_character(
        user.id, knife["id"], capo.id
    )
    assert result["success"] is True
    assert "Куплено оружие" in result["message"]

    resources = await user_resource_crud.get_by_user(db_session, user.id)
    assert resources.money == 1000 - knife["cost_money"]


@pytest.mark.asyncio
async def test_buy_tool_for_character(db_session):
    """Buy tool for a specific character."""
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(9103, "tool_buyer")

    capo = await character_crud.create(db_session, {
        "user_id": user.id,
        "name": "ToolCapo",
        "power": 10,
        "intellect": 10,
        "agility": 10,
        "loyalty": 10,
        "is_busy": False,
    })

    await _seed_shop(db_session)
    shop_svc = ShopService(db_session)
    items = await shop_svc.list_available()
    lockpick = next(i for i in items if i["item_type"] == "tool")

    result = await shop_svc.buy_tool_for_character(
        user.id, lockpick["id"], capo.id
    )
    assert result["success"] is True
    assert "Куплен инструмент" in result["message"]


@pytest.mark.asyncio
async def test_buy_weapon_wrong_character(db_session):
    """Should fail if character doesn't belong to user."""
    svc = UserService(db_session)
    user1 = await svc.get_or_create_by_telegram(9104, "victim")
    user2 = await svc.get_or_create_by_telegram(9105, "thief")

    capo = await character_crud.create(db_session, {
        "user_id": user1.id,
        "name": "VictimCapo",
        "power": 10,
        "intellect": 10,
        "agility": 10,
        "loyalty": 10,
        "is_busy": False,
    })

    await _seed_shop(db_session)
    shop_svc = ShopService(db_session)
    items = await shop_svc.list_available()
    knife = next(i for i in items if i["item_type"] == "weapon")

    result = await shop_svc.buy_weapon_for_character(
        user2.id, knife["id"], capo.id
    )
    assert result["success"] is False
    assert "не ваш" in result["message"].lower() or "not found" in result[
        "message"
    ].lower()

async def _seed_shop(db_session):
    """Seed shop items for tests."""
    from core.database.models.enums import (
        CharacterRole,
        CharacterTrait,
        ShopItemType,
    )
    from crud.other_crud import shop_item_crud

    existing = await shop_item_crud.list(db_session)
    if existing:
        return
    items = [
        {
            "name": "Боевик",
            "description": "Крепкий парень.",
            "item_type": ShopItemType.CHARACTER,
            "cost_money": 500,
            "cost_influence": 0,
            "role": CharacterRole.THUG,
            "trait": CharacterTrait.HOT,
            "base_power": 20,
            "base_intellect": 5,
            "base_agility": 10,
            "base_loyalty": 10,
            "display_order": 1,
        },
        {
            "name": "Нож",
            "description": "Тихий и надёжный.",
            "item_type": ShopItemType.WEAPON,
            "cost_money": 150,
            "cost_influence": 0,
            "bonus_power": 3,
            "display_order": 10,
        },
        {
            "name": "Отмычки",
            "description": "Для тихого проникновения.",
            "item_type": ShopItemType.TOOL,
            "cost_money": 200,
            "cost_influence": 0,
            "bonus_intellect": 2,
            "bonus_agility": 3,
            "display_order": 20,
        },
    ]
    for data in items:
        await shop_item_crud.create(db_session, data)
    await db_session.commit()
