"""
Telegram notifier for BPR&D meeting service.
Sends alerts for items needing Russell's attention.
"""

import logging

import httpx

from config import settings
from models.meeting import MeetingResponse

logger = logging.getLogger(__name__)


async def send_meeting_notification(response: MeetingResponse) -> bool:
    """Send a Telegram notification with meeting highlights."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.info("Telegram not configured, skipping notification")
        return False

    # Build notification message
    lines = [f"*{response.meeting_type.replace('_', ' ').title()}* completed\n"]

    if response.key_decisions:
        lines.append("*Key Decisions:*")
        for d in response.key_decisions[:3]:
            lines.append(f"  {d}")
        lines.append("")

    if response.action_items:
        russell_items = [a for a in response.action_items if a.assigned_to.lower() == "russell"]
        if russell_items:
            lines.append("*Your Action Items:*")
            for a in russell_items:
                lines.append(f"  [{a.priority}] {a.task}")
            lines.append("")

    if response.handoffs:
        russell_handoffs = [h for h in response.handoffs if h.assigned_to.lower() == "russell"]
        if russell_handoffs:
            lines.append("*Handoffs for You:*")
            for h in russell_handoffs:
                lines.append(f"  [{h.priority}] {h.title}")
            lines.append("")

    cost = response.cost_estimate
    lines.append(f"Cost: ${cost.cost_usd:.4f} | {cost.execution_time_seconds:.0f}s")

    message = "\n".join(lines)

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Telegram notification sent")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Telegram notification failed: {e}")
            return False
