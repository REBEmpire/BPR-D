"""
Daily Briefing meeting type for BPR&D meeting service.
Phase 1 implementation: Morning sync with repo review, priority setting, action items.

Phases: Context → Grok Opens → Agent Round (1) → Grok Synthesizes → Grok Closes
"""

import logging
from datetime import datetime

from agents.registry import RegisteredAgent
from models.meeting import MeetingResponse, CostEstimate
from orchestrator.engine import MeetingEngine
from output.parser import parse_synthesis
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class DailyBriefing:
    meeting_type = "daily_briefing"

    async def execute(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
    ) -> MeetingResponse:
        meeting_id = f"daily_briefing-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        cost_tracker.meeting_id = meeting_id

        logger.info(f"Executing Daily Briefing: {meeting_id}")

        engine = MeetingEngine(
            agents=agents,
            cost_tracker=cost_tracker,
            meeting_type=self.meeting_type,
            agenda=agenda,
        )

        synthesis_raw, transcript = await engine.run()

        # Parse structured output from Grok's synthesis
        parsed = parse_synthesis(synthesis_raw)

        # Build the full meeting notes (transcript + synthesis)
        notes = f"# BPR&D Daily Briefing — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
        notes += transcript.to_markdown()
        if parsed.get("meeting_notes"):
            notes += f"\n---\n\n## Summary\n\n{parsed['meeting_notes']}\n"
        if parsed.get("for_russell"):
            notes += f"\n## For Russell\n\n{parsed['for_russell']}\n"

        return MeetingResponse(
            success=True,
            meeting_id=meeting_id,
            meeting_type=self.meeting_type,
            notes=notes,
            handoffs=parsed.get("handoffs", []),
            action_items=parsed.get("action_items", []),
            key_decisions=parsed.get("key_decisions", []),
            cost_estimate=CostEstimate(**cost_tracker.to_dict()),
        )
