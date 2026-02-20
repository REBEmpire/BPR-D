"""
Standalone entry point for the Render cron job: bprd-daily-team-meeting.
Invoked via: python -m scripts.run_daily_team_meeting

Runs a single Daily Briefing meeting and exits.
Mirrors main.py:execute_meeting() without requiring FastAPI.
"""

import asyncio
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("bprd-cron-daily")


async def main():
    from agents.registry import resolve_participants, load_agents, is_abacus_available
    from config import settings
    from meetings import MEETING_TYPES
    from models.meeting import MeetingRequest, MeetingType, CostEstimate
    from output.github_writer import commit_meeting_results
    from output.notifier import send_meeting_notification
    from utils.cost_tracker import CostTracker, load_monthly_spend, save_cost_log

    logger.info("BPR&D Daily Team Meeting — cron entry point")

    # Budget check
    monthly = load_monthly_spend()
    if monthly >= settings.MONTHLY_BUDGET_CAP:
        logger.error("Monthly budget cap reached: $%.2f. Skipping.", monthly)
        return

    request = MeetingRequest(meeting_type=MeetingType.DAILY_BRIEFING)
    meeting_type_str = request.meeting_type.value
    meeting_id = f"{meeting_type_str}-cron-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    # Check meeting type is implemented
    meeting_cls = MEETING_TYPES.get(meeting_type_str)
    if not meeting_cls:
        logger.error("Meeting type '%s' not implemented.", meeting_type_str)
        sys.exit(1)

    # Resolve and filter participants
    participant_names = resolve_participants(request.participants, meeting_type_str)
    available = []
    for name in participant_names:
        if name == "grok" and not settings.XAI_API_KEY:
            logger.error("Grok requested but XAI_API_KEY missing.")
            continue
        if name == "claude" and not settings.ANTHROPIC_API_KEY:
            logger.warning("Claude requested but ANTHROPIC_API_KEY missing. Skipping.")
            continue
        if name == "gemini" and not settings.GEMINI_API_KEY:
            logger.warning("Gemini requested but GEMINI_API_KEY missing. Skipping.")
            continue
        if name == "abacus" and not is_abacus_available():
            logger.warning("Abacus requested but API key missing. Skipping.")
            continue
        available.append(name)

    if not available:
        logger.error("No agents available (check API keys).")
        sys.exit(1)

    agents = await load_agents(available)
    if not agents:
        logger.error("No agents could be loaded.")
        sys.exit(1)

    tracker = CostTracker(meeting_id=meeting_id)

    try:
        meeting = meeting_cls()
        response = await meeting.execute(
            agents=agents,
            cost_tracker=tracker,
            agenda="",
        )

        save_cost_log(tracker)
        tracker.log_summary()

        try:
            commit_ok, notes_path = await commit_meeting_results(response)
            if commit_ok and notes_path:
                logger.info("Session committed: %s", notes_path)
        except Exception as e:
            logger.error("GitHub commit failed: %s", e)

        try:
            await send_meeting_notification(response)
        except Exception as e:
            logger.error("Notification failed: %s", e)

        logger.info("Daily meeting %s completed successfully.", meeting_id)

    except Exception as e:
        logger.error("Meeting %s failed: %s", meeting_id, e, exc_info=True)
        save_cost_log(tracker)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
