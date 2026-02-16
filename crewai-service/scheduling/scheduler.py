"""
Meeting scheduler for BPR&D meeting service.
Uses APScheduler to trigger meetings on cron schedules.
Phase 1: Daily Briefing only (Mon-Fri 07:47 AM PST).
Phase 2: Work Session Automation (Every 2 hours).
"""

import logging

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


async def _run_work_session():
    """Scheduled job: execute work session (handoff update)."""
    if _execute_meeting_fn is None:
        logger.error("Meeting execution function not set")
        return

    logger.info("Scheduler: triggering Work Session")
    try:
        from models.meeting import MeetingRequest, MeetingType
        # Default to Grok for now, or could rotate
        request = MeetingRequest(
            meeting_type=MeetingType.WORK_SESSION,
            participants=["grok"]
        )
        await _execute_meeting_fn(request)
    except Exception as e:
        logger.error(f"Scheduled Work Session failed: {e}", exc_info=True)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the meeting scheduler.

    Phase 1: Daily Briefing only.
    Phase 2: Work Session Automation.
    """
    scheduler = AsyncIOScheduler(timezone="US/Pacific")

    # Phase 1: Daily Briefing — Mon-Fri 07:47 AM PST
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

    # Phase 2: Work Session — Every 2 hours
    scheduler.add_job(
        _run_work_session,
        trigger=CronTrigger(hour="*/2", timezone="US/Pacific"),
        id="work_session",
        name="Automated Work Session (Every 2 hours)",
        replace_existing=True,
    )

    logger.info("Scheduler configured with Phase 1 & 2 jobs")
    return scheduler
