"""Background tasks for automatic mission completion."""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from core.database.models import UserMission
from core.database.models.enums import MissionStatus
from services.mission_service import MissionService

logger = logging.getLogger(__name__)

# Check interval in seconds
CHECK_INTERVAL = 30


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
                logger.info(f"Found {len(expired_missions)} expired missions to complete.")

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


async def background_tasks_loop():
    """Main loop for background tasks."""
    logger.info("Starting background tasks loop.")
    while True:
        try:
            await complete_expired_missions()
        except Exception as e:
            logger.error(f"Error in background tasks loop iteration: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)
