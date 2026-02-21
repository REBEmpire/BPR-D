"""
Meeting scheduler for BPR&D meeting service.
Uses APScheduler to trigger the Daily Briefing on cron schedule.
Manual team meetings are triggered via /api/v1/meetings/manual-trigger.
"""

import logging
import os
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Lazy import to avoid circular deps
_execute_meeting_fn = None


def _set_execute_fn(fn):
    """Set the meeting execution function (called from main.py startup)."""
    global _execute_meeting_fn
    _execute_meeting_fn = fn


async def _run_daily_briefing():
    """Scheduled job: execute daily briefing."""
    if _execute_meeting_fn is None:
        logger.error("Meeting execution function not set")
        return

    logger.info("Scheduler: triggering Daily Briefing")
    try:
        from models.meeting import MeetingRequest, MeetingType
        request = MeetingRequest(meeting_type=MeetingType.DAILY_BRIEFING)
        await _execute_meeting_fn(request)
    except Exception as e:
        logger.error(f"Scheduled Daily Briefing failed: {e}", exc_info=True)


async def execute_solo_work_session():
    """Scheduled job: execute a solo work session with a random agent."""
    if _execute_meeting_fn is None:
        logger.error("Meeting execution function not set")
        return

    # Randomly select an agent
    agents = ["grok", "claude", "gemini", "abacus"]
    agent = random.choice(agents)

    logger.info(f"Scheduler: triggering Solo Work Session for {agent}")
    try:
        from models.meeting import MeetingRequest, MeetingType
        request = MeetingRequest(
            meeting_type=MeetingType.WORK_SESSION,
            participants=[agent]
        )
        await _execute_meeting_fn(request)
    except Exception as e:
        logger.error(f"Scheduled Work Session failed: {e}", exc_info=True)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the meeting scheduler.

    Daily Briefing only — Mon-Fri 07:47 AM PST.
    Manual team meetings are triggered via the /api/v1/meetings/manual-trigger endpoint.
    """
    scheduler = AsyncIOScheduler(timezone="US/Pacific")

    scheduler.add_job(
        _run_daily_briefing,
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour=7,
            minute=47,
            timezone="US/Pacific",
        ),
        id="daily_briefing",
        name="Daily Briefing (Mon-Fri 07:47 AM PST)",
        replace_existing=True,
    )

    logger.info("Scheduler configured with Daily Briefing (Mon-Fri 07:47 AM PST)")

    # --- Work Sessions (Optional) ---
    if os.getenv("ENABLE_WORK_SESSIONS", "false").lower() == "true":
        scheduler.add_job(
            execute_solo_work_session,
            "interval",
            minutes=30,
            id="work_session_stagger",
            name="Solo Work Session (Every 30 mins)",
            replace_existing=True,
        )
        logger.info("Scheduler configured with Work Sessions (Every 30 mins)")
    else:
        logger.info("Work sessions DISABLED per HiC directive.")

    return scheduler
