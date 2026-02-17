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


def _build_agent_instructions(
    parsed: dict,
    participating_agents: list[str],
    meeting_date: str,
) -> dict[str, str]:
    """Build per-agent handoff.md content from parsed daily briefing output.

    Extracts action items and handoffs assigned to each agent and formats
    them as a simple task checklist for _agents/[agent]/handoff.md.
    """
    agent_tasks: dict[str, list[str]] = {name: [] for name in participating_agents}

    for item in parsed.get("action_items", []):
        assignee = item.assigned_to.lower()
        if assignee in agent_tasks:
            priority_marker = "!" if item.priority in ("high", "critical") else ""
            deadline_str = f" (due: {item.deadline})" if item.deadline else ""
            agent_tasks[assignee].append(
                f"- [ ] {priority_marker}{item.task}{deadline_str}"
            )

    for handoff in parsed.get("handoffs", []):
        assignee = handoff.assigned_to.lower()
        if assignee in agent_tasks:
            agent_tasks[assignee].append(
                f"- [ ] [Escalation] {handoff.title} — see `_handoffs/{handoff.task_id}.md`"
            )

    instructions = {}
    for agent_name, tasks in agent_tasks.items():
        if not tasks:
            continue

        lines = [
            f"# {agent_name.title()} — Operational Tasks",
            f"**Source:** Daily Briefing {meeting_date}",
            f"**Last Updated:** {meeting_date}",
            "",
            "## Active Tasks",
            "",
        ]
        lines.extend(tasks)
        lines.append("")
        lines.append("---")
        lines.append("*Updated automatically by meeting engine.*")

        instructions[agent_name] = "\n".join(lines)

    return instructions


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

        # Build meeting notes (transcript only — summary rendered separately at top)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        notes = f"# BPR&D Daily Briefing — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
        notes += transcript.to_markdown()

        # Build per-agent task checklists from action items and handoffs
        agent_instructions = _build_agent_instructions(
            parsed=parsed,
            participating_agents=list(agents.keys()),
            meeting_date=date_str,
        )

        return MeetingResponse(
            success=True,
            meeting_id=meeting_id,
            meeting_type=self.meeting_type,
            notes=notes,
            summary=parsed.get("meeting_notes", ""),
            for_russell=parsed.get("for_russell", ""),
            handoffs=parsed.get("handoffs", []),
            action_items=parsed.get("action_items", []),
            key_decisions=parsed.get("key_decisions", []),
            agent_instructions=agent_instructions,
            cost_estimate=CostEstimate(**cost_tracker.to_dict()),
        )
