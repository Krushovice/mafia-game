"""Background tasks for automatic mission completion and passive income."""

import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database.db_helper import db_helper
from core.database.models import Mission, User, UserMission
from core.database.models.enums import MissionStatus, MissionType, NotificationType
from services.mission_service import MissionService
from services.notification_service import (
    enqueue_notification,
    format_flash_mission,
    format_mission_completed,
    format_mission_event,
    format_mission_failed,
)
from services.territory_service import TerritoryService

logger = logging.getLogger(__name__)

# Check interval in seconds (10 minutes for passive income)
CHECK_INTERVAL = 600

FLASH_MIN_INTERVAL = 4 * 3600   # 4 hours
FLASH_MAX_INTERVAL = 6 * 3600   # 6 hours
FLASH_DURATION = 2 * 3600       # flash mission lives 2 hours


async def complete_expired_missions():
    """Find and complete missions that have passed their end time.

    После каждого автозавершения добавляем запись в очередь уведомлений,
    чтобы бот отправил пуш в Telegram.
    """
    try:
        async with AsyncSession(bind=db_helper.engine) as session:
            result = await session.execute(
                select(UserMission)
                .options(selectinload(UserMission.mission))
                .where(
                    UserMission.status == MissionStatus.IN_PROGRESS,
                    UserMission.ends_at < datetime.now(timezone.utc),
                )
            )
            expired_missions = result.scalars().all()

            if expired_missions:
                logger.info(
                    f"Found {len(expired_missions)} expired missions to complete."
                )

            for user_mission in expired_missions:
                mission_name = (
                    user_mission.mission.name if user_mission.mission else "Миссия"
                )
                user_id = user_mission.user_id
                um_id = user_mission.id

                try:
                    svc = MissionService(session)
                    res = await svc.complete_mission(um_id)

                    if not res.get("success"):
                        logger.warning(
                            f"Failed to auto-complete mission {um_id}: {res.get('message')}"
                        )
                        continue

                    logger.info(f"Auto-completed mission {um_id} for user {user_id}")

                    await _enqueue_completion_notification(
                        session, user_id, um_id, mission_name, res
                    )

                except Exception as e:
                    logger.error(f"Error completing mission {um_id}: {e}")
                    await session.rollback()
                    continue

            await session.commit()

    except Exception as e:
        logger.error(f"Error in complete_expired_missions loop: {e}")


async def _enqueue_completion_notification(
    session: AsyncSession,
    user_id: int,
    user_mission_id: int,
    mission_name: str,
    result: dict,
) -> None:
    """Поставить в очередь нужный тип уведомления на основе результата `complete_mission`."""
    if result.get("event_triggered"):
        body = format_mission_event(mission_name, result.get("event_description") or "")
        await enqueue_notification(
            session,
            user_id=user_id,
            notification_type=NotificationType.MISSION_EVENT,
            body=body,
            payload={
                "user_mission_id": user_mission_id,
                "event_log_id": result.get("event_log_id"),
                "event_type": result.get("event_type"),
            },
        )
        return

    mission_succeeded = (
        result.get("reward_money", 0) > 0 or result.get("reward_influence", 0) > 0
    )
    if mission_succeeded:
        body = format_mission_completed(mission_name, result)
        notif_type = NotificationType.MISSION_COMPLETED
    else:
        body = format_mission_failed(mission_name)
        notif_type = NotificationType.MISSION_FAILED

    await enqueue_notification(
        session,
        user_id=user_id,
        notification_type=notif_type,
        body=body,
        payload={"user_mission_id": user_mission_id},
    )


async def collect_passive_income_for_all_users():
    """Collect passive income for all users with captured territories.

    Runs every 10 minutes to calculate and apply income based on time passed since last tick.
    Handles online (full income) and offline (>15 min gap, 5% reduced income) states.
    """
    try:
        async with AsyncSession(bind=db_helper.engine) as session:
            # Get all users with territories
            result = await session.execute(
                select(UserMission).where(
                    UserMission.user_id.isnot(None),
                    UserMission.status == MissionStatus.COMPLETED,
                )
            )
            user_ids = {
                um.user_id for um in result.scalars().all() if um.user_id is not None
            }

            if not user_ids:
                logger.info("No users found with completed missions")
                return

            logger.info(f"Found {len(user_ids)} users to process passive income for")

            total_money_gained = 0
            total_influence_gained = 0

            for user_id in user_ids:
                try:
                    svc = TerritoryService(session)
                    result = await svc.collect_passive_income(user_id)

                    if result["money_gained"] > 0 or result["influence_gained"] > 0:
                        logger.info(
                            f"User {user_id}: +{result['money_gained']}💰 "
                            f"+{result['influence_gained']}🌐 (playtime: {result['active_playtime']}min)"
                        )

                        total_money_gained += result["money_gained"]
                        total_influence_gained += result["influence_gained"]

                except Exception as e:
                    logger.error(
                        f"Error collecting passive income for user {user_id}: {e}"
                    )
                    await session.rollback()

            if total_money_gained > 0 or total_influence_gained > 0:
                await session.commit()
                logger.info(
                    f"Passive income collection complete: "
                    f"+{total_money_gained}💰 +{total_influence_gained}🌐 for {len(user_ids)} users"
                )

    except Exception as e:
        logger.error(f"Error in collect_passive_income_for_all_users loop: {e}")


async def spawn_flash_mission() -> None:
    """Create one global flash UserMission and notify all users.

    Picks a random mission as template, multiplies rewards x2.5, sets
    available_until=now+2h, user_id=None (global — any player can claim it).
    """
    try:
        async with AsyncSession(bind=db_helper.engine) as session:
            # Clean up stale expired flash missions first
            now = datetime.now(timezone.utc)
            stale = await session.execute(
                select(UserMission).where(
                    UserMission.mission_type == MissionType.FLASH,
                    UserMission.user_id.is_(None),
                    UserMission.available_until < now,
                )
            )
            for um in stale.scalars().all():
                await session.delete(um)

            # Pick random mission template
            result = await session.execute(
                select(Mission).order_by(func.random()).limit(1)
            )
            mission = result.scalar_one_or_none()
            if not mission:
                logger.warning("spawn_flash_mission: no missions in DB, skipping")
                return

            available_until = now + timedelta(seconds=FLASH_DURATION)
            flash_um = UserMission(
                user_id=None,
                mission_id=mission.id,
                status=MissionStatus.PENDING,
                mission_type=MissionType.FLASH,
                available_until=available_until,
                success_chance=75,
                reward_money=int(mission.reward_money * 2.5),
                reward_influence=int(mission.reward_influence * 2.5),
                wanted_increase=int(mission.wanted_increase * 1.5),
                location_name=mission.name,
                position_x=0,
                position_y=0,
            )
            session.add(flash_um)
            await session.flush()
            flash_id = flash_um.id

            # Notify all users
            users_result = await session.execute(select(User))
            users = users_result.scalars().all()

            expires_text = available_until.strftime("%H:%M UTC")
            body = format_flash_mission(mission.name, expires_text)

            for user in users:
                await enqueue_notification(
                    session,
                    user_id=user.id,
                    notification_type=NotificationType.FLASH_MISSION,
                    body=body,
                    payload={"flash_mission_id": flash_id},
                )

            await session.commit()
            logger.info(
                f"Flash mission spawned: '{mission.name}' "
                f"(id={flash_id}), notified {len(users)} users, "
                f"expires {available_until.isoformat()}"
            )
    except Exception as e:
        logger.error(f"Error in spawn_flash_mission: {e}")


async def flash_mission_loop() -> None:
    """Spawn flash missions every 4-6 hours."""
    while True:
        delay = random.randint(FLASH_MIN_INTERVAL, FLASH_MAX_INTERVAL)
        logger.info(f"Next flash mission in {delay / 3600:.1f}h")
        await asyncio.sleep(delay)
        await spawn_flash_mission()


async def background_tasks_loop():
    """Main loop for background tasks."""
    logger.info("Starting background tasks loop.")

    asyncio.create_task(flash_mission_loop())

    # Run passive income collection every 10 minutes (600 seconds)
    while True:
        try:
            await collect_passive_income_for_all_users()
        except Exception as e:
            logger.error(f"Error in background tasks loop iteration: {e}")

        await asyncio.sleep(CHECK_INTERVAL)
