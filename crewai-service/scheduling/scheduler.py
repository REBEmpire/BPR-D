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
        # Default participants includes Abacus if available (checked in registry)
        request = MeetingRequest(meeting_type=MeetingType.DAILY_BRIEFING)
        await _execute_meeting_fn(request)
    except Exception as e:
        logger.error(f"Scheduled Daily Briefing failed: {e}", exc_info=True)


async def _trigger_work_session(agent_name: str):
    """Internal helper to trigger a work session."""
    if _execute_meeting_fn is None:
        logger.error("Meeting execution function not set")
        return

    logger.info(f"Scheduler: triggering Work Session for {agent_name}")
    try:
        from models.meeting import MeetingRequest, MeetingType
        request = MeetingRequest(
            meeting_type=MeetingType.WORK_SESSION,
            participants=[agent_name]
        )
        await _execute_meeting_fn(request)
    except Exception as e:
        logger.error(f"Scheduled Work Session for {agent_name} failed: {e}", exc_info=True)


async def _run_work_session_grok():
    await _trigger_work_session("grok")


async def _run_work_session_claude():
    await _trigger_work_session("claude")


async def _run_work_session_gemini():
    await _trigger_work_session("gemini")


async def _run_work_session_abacus():
    await _trigger_work_session("abacus")


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

    # Phase 2: Work Session — Staggered Schedule (Every 2 hours)
    # 1. Grok: Even hours (0, 2, 4...) at 00
    scheduler.add_job(
        _run_work_session_grok,
        trigger=CronTrigger(hour="0-23/2", minute=0, timezone="US/Pacific"),
        id="work_session_grok",
        name="Work Session: Grok (Even hours :00)",
        replace_existing=True,
    )

    # 2. Claude: Even hours (0, 2, 4...) at 30
    scheduler.add_job(
        _run_work_session_claude,
        trigger=CronTrigger(hour="0-23/2", minute=30, timezone="US/Pacific"),
        id="work_session_claude",
        name="Work Session: Claude (Even hours :30)",
        replace_existing=True,
    )

    # 3. Abacus: Odd hours (1, 3, 5...) at 00
    scheduler.add_job(
        _run_work_session_abacus,
        trigger=CronTrigger(hour="1-23/2", minute=0, timezone="US/Pacific"),
        id="work_session_abacus",
        name="Work Session: Abacus (Odd hours :00)",
        replace_existing=True,
    )

    # 4. Gemini: Odd hours (1, 3, 5...) at 30
    scheduler.add_job(
        _run_work_session_gemini,
        trigger=CronTrigger(hour="1-23/2", minute=30, timezone="US/Pacific"),
        id="work_session_gemini",
        name="Work Session: Gemini (Odd hours :30)",
        replace_existing=True,
    )

    logger.info("Scheduler configured with Daily Briefing and Staggered Work Sessions (Grok, Claude, Abacus, Gemini)")
    return scheduler
