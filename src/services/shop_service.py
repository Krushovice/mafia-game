"""Shop service — покупка бойцов и экипировки."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Character, ShopItem
from core.database.models.enums import ShopItemType
from crud.other_crud import (
    character_crud,
    shop_item_crud,
    tool_crud,
    user_resource_crud,
    weapon_crud,
)


class ShopService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.shop_item_crud = shop_item_crud
        self.user_resource_crud = user_resource_crud

    async def list_available(self) -> list[dict]:
        """Список доступных товаров."""
        items = await shop_item_crud.list_available(self.session)
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "item_type": item.item_type.value,
                "cost_money": item.cost_money,
                "cost_influence": item.cost_influence,
                "role": item.role.value if item.role else None,
                "base_power": item.base_power,
                "base_intellect": item.base_intellect,
                "base_agility": item.base_agility,
                "bonus_power": item.bonus_power,
                "bonus_intellect": item.bonus_intellect,
                "bonus_agility": item.bonus_agility,
            }
            for item in items
        ]

    async def buy_item(self, user_id: int, item_id: int) -> dict:
        """Купить товар из магазина."""
        item = await shop_item_crud.get(self.session, item_id)
        if not item:
            return {"success": False, "message": "Товар не найден"}

        if not item.is_available:
            return {"success": False, "message": "Товар недоступен"}

        resources = await self.user_resource_crud.get_by_user(self.session, user_id)
        if not resources:
            return {"success": False, "message": "Ресурсы не найдены"}

        if resources.money < item.cost_money:
            return {
                "success": False,
                "message": (
                    f"Нужно {item.cost_money} монет, " f"есть {resources.money}"
                ),
            }
        if resources.influence < item.cost_influence:
            return {
                "success": False,
                "message": (
                    f"Нужно {item.cost_influence} влияния, "
                    f"есть {resources.influence}"
                ),
            }

        # Списываем ресурсы
        resources.money -= item.cost_money
        resources.influence -= item.cost_influence

        if item.item_type == ShopItemType.CHARACTER:
            return await self._buy_character(user_id, item)
        if item.item_type == ShopItemType.WEAPON:
            return await self._buy_weapon(user_id, item)
        if item.item_type == ShopItemType.TOOL:
            return await self._buy_tool(user_id, item)

        return {"success": False, "message": "Неизвестный тип товара"}

    async def _buy_character(self, user_id: int, item: ShopItem) -> dict:
        """Купить персонажа."""
        if self.session.in_transaction():
            character = await character_crud.create(
                self.session,
                {
                    "user_id": user_id,
                    "name": item.name,
                    "role": item.role,
                    "trait": item.trait,
                    "power": item.base_power,
                    "intellect": item.base_intellect,
                    "agility": item.base_agility,
                    "loyalty": item.base_loyalty,
                    "is_busy": False,
                },
                commit=False,
            )
            item.buyer_id = user_id
            return {
                "success": True,
                "message": f"Куплен боец: {item.name}",
                "character_id": character.id,
            }
        else:
            async with self.session.begin():
                character = await character_crud.create(
                    self.session,
                    {
                        "user_id": user_id,
                        "name": item.name,
                        "role": item.role,
                        "trait": item.trait,
                        "power": item.base_power,
                        "intellect": item.base_intellect,
                        "agility": item.base_agility,
                        "loyalty": item.base_loyalty,
                        "is_busy": False,
                    },
                    commit=False,
                )
                item.buyer_id = user_id
                return {
                    "success": True,
                    "message": f"Куплен боец: {item.name}",
                    "character_id": character.id,
                }

    async def _buy_weapon(self, user_id: int, item: ShopItem) -> dict:
        """Купить оружие. Нужно выбрать персонажа-владельца."""
        # Для оружия нужен character_id — вернём ошибку
        return {
            "success": False,
            "message": (
                "Для покупки оружия укажите character_id "
                "через POST /shop/buy/{item_id}?character_id=N"
            ),
        }

    async def buy_weapon_for_character(
        self, user_id: int, item_id: int, character_id: int
    ) -> dict:
        """Купить оружие для конкретного персонажа."""
        item = await shop_item_crud.get(self.session, item_id)
        if not item:
            return {"success": False, "message": "Товар не найден"}

        if item.item_type != ShopItemType.WEAPON:
            return {"success": False, "message": "Это не оружие"}

        resources = await self.user_resource_crud.get_by_user(self.session, user_id)
        if not resources:
            return {"success": False, "message": "Ресурсы не найдены"}

        if resources.money < item.cost_money:
            return {
                "success": False,
                "message": (
                    f"Нужно {item.cost_money} монет, " f"есть {resources.money}"
                ),
            }

        # Проверяем что персонаж принадлежит пользователю
        character_result = await self.session.execute(
            select(Character).where(
                Character.id == character_id, Character.user_id == user_id
            )
        )
        character = character_result.scalar_one_or_none()
        if not character:
            return {
                "success": False,
                "message": "Персонаж не найден или не ваш",
            }

        resources.money -= item.cost_money

        if self.session.in_transaction():
            weapon = await weapon_crud.create(
                self.session,
                {
                    "name": item.name,
                    "bonus_power": item.bonus_power,
                    "owner_id": character.id,
                },
                commit=False,
            )
            item.buyer_id = user_id
            return {
                "success": True,
                "message": f"Куплено оружие: {item.name}",
                "weapon_id": weapon.id,
            }
        else:
            async with self.session.begin():
                weapon = await weapon_crud.create(
                    self.session,
                    {
                        "name": item.name,
                        "bonus_power": item.bonus_power,
                        "owner_id": character.id,
                    },
                    commit=False,
                )
                item.buyer_id = user_id
                return {
                    "success": True,
                    "message": f"Куплено оружие: {item.name}",
                    "weapon_id": weapon.id,
                }

    async def buy_tool_for_character(
        self, user_id: int, item_id: int, character_id: int
    ) -> dict:
        """Купить инструмент для конкретного персонажа."""
        item = await shop_item_crud.get(self.session, item_id)
        if not item:
            return {"success": False, "message": "Товар не найден"}

        if item.item_type != ShopItemType.TOOL:
            return {"success": False, "message": "Это не инструмент"}

        resources = await self.user_resource_crud.get_by_user(self.session, user_id)
        if not resources:
            return {"success": False, "message": "Ресурсы не найдены"}

        if resources.money < item.cost_money:
            return {
                "success": False,
                "message": (
                    f"Нужно {item.cost_money} монет, " f"есть {resources.money}"
                ),
            }

        character_result = await self.session.execute(
            select(Character).where(
                Character.id == character_id, Character.user_id == user_id
            )
        )
        character = character_result.scalar_one_or_none()
        if not character:
            return {
                "success": False,
                "message": "Персонаж не найден или не ваш",
            }

        resources.money -= item.cost_money

        if self.session.in_transaction():
            tool = await tool_crud.create(
                self.session,
                {
                    "name": item.name,
                    "bonus_intellect": item.bonus_intellect,
                    "bonus_agility": item.bonus_agility,
                    "owner_id": character.id,
                },
                commit=False,
            )
            item.buyer_id = user_id
            return {
                "success": True,
                "message": f"Куплен инструмент: {item.name}",
                "tool_id": tool.id,
            }
        else:
            async with self.session.begin():
                tool = await tool_crud.create(
                    self.session,
                    {
                        "name": item.name,
                        "bonus_intellect": item.bonus_intellect,
                        "bonus_agility": item.bonus_agility,
                        "owner_id": character.id,
                    },
                    commit=False,
                )
                item.buyer_id = user_id
                return {
                    "success": True,
                    "message": f"Куплен инструмент: {item.name}",
                    "tool_id": tool.id,
                }
