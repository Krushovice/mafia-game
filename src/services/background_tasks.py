"""Background tasks for automatic mission completion and passive income."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models import UserMission
from core.database.models.enums import MissionStatus
from services.mission_service import MissionService
from services.territory_service import TerritoryService

logger = logging.getLogger(__name__)

# Check interval in seconds (10 minutes for passive income)
CHECK_INTERVAL = 600


async def complete_expired_missions():
    """Find and complete missions that have passed their end time."""
    try:
        async with AsyncSession(bind=db_helper.engine) as session:
            # Find expired missions
            result = await session.execute(
                select(UserMission).where(
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
                try:
                    # Create service instance for this mission
                    # Note: We pass the session that loaded the user_mission object
                    # But since complete_mission might commit, we need to be careful with scope.
                    # The service uses its own session logic, but here we just call the logic.
                    # To avoid session conflicts, let's create a new service with the current session
                    # or better, just call the logic if it's transaction-safe.
                    # However, MissionService.complete_mission expects to commit.
                    # Since we are in a `with` block (autocommit=False), we need to ensure it works.

                    # Better approach: Create a NEW session for the service logic to isolate commits
                    # and avoid messing with the current selection loop's state if possible,
                    # or just handle it carefully.

                    # Actually, simplest is to pass the ID to a helper that handles its own session scope?
                    # No, let's just use the service. But we must ensure the session is ready.

                    svc = MissionService(session)
                    res = await svc.complete_mission(user_mission.id)

                    if res.get("success"):
                        logger.info(
                            f"Auto-completed mission {user_mission.id} for user {user_mission.user_id}"
                        )
                    else:
                        logger.warning(
                            f"Failed to auto-complete mission {user_mission.id}: {res.get('message')}"
                        )

                except Exception as e:
                    logger.error(f"Error completing mission {user_mission.id}: {e}")
                    await session.rollback()
                    continue

            await session.commit()

    except Exception as e:
        logger.error(f"Error in complete_expired_missions loop: {e}")


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


async def background_tasks_loop():
    """Main loop for background tasks."""
    logger.info("Starting background tasks loop.")

    # Run passive income collection every 10 minutes (600 seconds)
    while True:
        try:
            await collect_passive_income_for_all_users()
        except Exception as e:
            logger.error(f"Error in background tasks loop iteration: {e}")

        await asyncio.sleep(CHECK_INTERVAL)
