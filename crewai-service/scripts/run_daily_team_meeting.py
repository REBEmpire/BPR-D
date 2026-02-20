import asyncio
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.registry import load_agents
from meetings.daily_briefing import DailyBriefing
from utils.cost_tracker import CostTracker
from output.github_writer import commit_meeting_results
from output.notifier import send_meeting_notification
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("daily-cron")

async def main():
    logger.info("Starting Daily Team Meeting Cron Job")

    # Load agents
    participants = ["grok", "claude", "gemini", "abacus"]
    agents = await load_agents(participants)

    if not agents:
        logger.error("Failed to load agents")
        return

    tracker = CostTracker(meeting_id=f"daily-cron-{datetime.utcnow().strftime('%Y%m%d')}")

    meeting = DailyBriefing()

    try:
        # Pull context from knowledge_system (briefly mentioned in prompt: "pulls today’s brief from knowledge_system/")
        # DailyBriefing logic usually handles context gathering via MeetingEngine.
        # We pass a generic agenda, and let MeetingEngine do the work.

        agenda = "Automated Daily Team Meeting: Review backlog, prioritized tasks from knowledge_system, and sync."

        response = await meeting.execute(
            agents=agents,
            cost_tracker=tracker,
            agenda=agenda
        )

        # Commit results
        success, path = await commit_meeting_results(response)
        if success:
            logger.info(f"Meeting results committed to {path}")
            response.session_path = path
        else:
            logger.error("Failed to commit meeting results")

        # Notify
        await send_meeting_notification(response)

        logger.info("Daily Team Meeting completed successfully")

    except Exception as e:
        logger.error(f"Meeting failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
