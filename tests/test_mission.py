from datetime import datetime, timedelta, timezone

import pytest

from crud.other_crud import character_crud, mission_crud, user_mission_crud
from services.mission_service import MissionService
from services.user_service import UserService


@pytest.mark.asyncio
async def test_start_and_complete_mission(db_session):
    # create user
    user_svc = UserService(db_session)
    user = await user_svc.get_or_create_by_telegram(9999, "missioner")

    # create character
    char = await character_crud.create(
        db_session,
        {
            "user_id": user.id,
            "name": "Joe",
            "power": 10,
            "intellect": 1,
            "agility": 1,
            "loyalty": 0,
            "is_busy": False,
        },
    )

    # create mission
    mission = await mission_crud.create(
        db_session,
        {
            "name": "Test",
            "description": "t",
            "duration": 1,
            "reward_money": 100,
            "reward_influence": 5,
            "difficulty": "easy",
            "slots": 1,
            "power_required": 5,
            "intellect_required": 0,
            "agility_required": 0,
        },
    )

    svc = MissionService(db_session)
    res = await svc.start_mission(user.id, mission.id, [char])
    assert res["success"] is True

    # fetch user_mission and set ends_at in past
    ums = await user_mission_crud.list(db_session)
    assert len(ums) == 1
    um = ums[0]
    um.ends_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.commit()

    complete_res = await svc.complete_mission(um.id)
    assert "success" in complete_res
    # character should be freed
    refreshed_char = await character_crud.get(db_session, char.id)
    assert refreshed_char.is_busy is False
