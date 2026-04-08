import pytest

from crud.other_crud import user_resource_crud
from services.user_service import UserService


@pytest.mark.asyncio
async def test_get_or_create_user(db_session):
    svc = UserService(db_session)
    user = await svc.get_or_create_by_telegram(12345, "tester")
    assert user is not None
    res = await user_resource_crud.get_by_user(db_session, user.id)
    assert res is not None
    assert res.money == 1000
    assert res.influence == 10
