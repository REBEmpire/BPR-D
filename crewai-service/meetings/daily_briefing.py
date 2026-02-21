"""
Daily Briefing meeting type for BPR&D meeting service.
7-round team meeting per team_meeting_protocol_v2.md.

Phases: Context → Grok Opens → 7 Agent Rounds → Debate → Grok Synthesizes → Context Updates → Grok Closes
"""

import asyncio
import logging
from datetime import datetime

from agents.registry import RegisteredAgent
from models.meeting import MeetingResponse, CostEstimate
from orchestrator.engine import MeetingEngine
from output.parser import parse_synthesis
from prompts.nervous_system_injector import NervousSystemInjector
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

DAILY_ROUND_TOPICS = [
    "Focus: Review + Outlook — Summarize yesterday's accomplishments "
    "(reference exact repo files/links). List any Daily Briefs by Jules worthy "
    "of content queue. Set today's direction and ask for team critique.",
    "Focus: Collaboration & Refinement — Critique yesterday, identify queue "
    "items, surface blockers, suggest research or content improvements. "
    "Open team discussion.",
    "Focus: Work Planning + Research Kickoff — Issue ambitious daily work items. "
    "Classify: small/routine → BPR&D_To_Do_List.md, large → dedicated project "
    "file. Propose research topics for the 6 pillars: Daily Briefs, Special "
    "Reports, Epstein Daily, Hive Blogging, Media/Content Creation, Social "
    "Media Marketing.",
    "Focus: Research Finalize + Content Creation Shift — Lock research topics, "
    "quality standards, and deliverables. Move to content creation department: "
    "discuss full implementation plan.",
    "Focus: Deep Content Creation Dive — Roast, refine, and elevate the content "
    "pipeline. Select 5 best daily briefs by Jules, reformat as Hive-ready "
    "Markdown with images, expand ~20% for readability.",
    "Focus: Assets & Financials — Review/update assets, income, expenses, "
    "financial tracking. Team adds input for record.",
    "Focus: Context Close — Deliver your key takeaways, active priorities, "
    "and context changes for your active.md update.",
]


class DailyBriefing:
    def __init__(self):
        self.meeting_type = "daily_briefing"

    async def execute(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
    ) -> MeetingResponse:
        meeting_id = f"daily_briefing-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        cost_tracker.meeting_id = meeting_id

        logger.info(f"Executing Daily Briefing: {meeting_id}")

        # Phase 0: Load nervous system — MUST be first (before MeetingEngine runs)
        ns_injector = NervousSystemInjector()
        await ns_injector.load()
        logger.info(
            f"Nervous system loaded for daily_briefing "
            f"({ns_injector.node_count} nodes)"
        )

        engine = MeetingEngine(
            agents=agents,
            cost_tracker=cost_tracker,
            meeting_type=self.meeting_type,
            agenda=agenda,
        )

        synthesis_raw, context_updates, transcript = await engine.run()

        # Parse structured output from Grok's synthesis
        parsed_data = parse_synthesis(synthesis_raw)

        # Build meeting notes (transcript only — summary rendered separately at top)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        notes = f"# BPR&D Daily Briefing — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
        notes += transcript.to_markdown()

        # Build per-agent task checklists from action items and handoffs
        agent_instructions = _build_agent_instructions(
            parsed_data=parsed_data,
            participating_agents=list(agents.keys()),
            meeting_date=date_str,
        )

        # Build final response object
        return MeetingResponse(
            success=True,
            meeting_id=meeting_id,
            meeting_type=self.meeting_type,
            notes=notes,
            summary=parsed_data.get("meeting_notes", ""),
            for_russell=parsed_data.get("for_russell", ""),
            handoffs=parsed_data.get("handoffs", []),
            action_items=parsed_data.get("action_items", []),
            key_decisions=parsed_data.get("key_decisions", []),
            agent_instructions=agent_instructions,
            context_updates=context_updates,
            cost_estimate=CostEstimate(**cost_tracker.to_dict()),
        )


def _build_agent_instructions(
    parsed_data: dict,
    participating_agents: list[str],
    meeting_date: str,
) -> dict[str, str]:
    """Build per-agent handoff.md content from parsed daily briefing output."""
    agent_tasks: dict[str, list[dict]] = {name: [] for name in participating_agents}

    # Process action items
    for item in parsed_data.get("action_items", []):
        assignee = item.assigned_to.lower()
        if assignee in agent_tasks:
            priority = "URGENT" if item.priority in ("high", "critical") else item.priority.title()
            agent_tasks[assignee].append({
                "task": item.task,
                "assigned_to": assignee.title(),
                "priority": priority,
                "status": "Pending",
                "due": item.deadline or "TBD",
            })

    # Process handoffs as escalations
    for handoff in parsed_data.get("handoffs", []):
        assignee = handoff.assigned_to.lower()
        if assignee in agent_tasks:
            agent_tasks[assignee].append({
                "task": f"[Escalation] {handoff.title} — see _handoffs/{handoff.task_id}.md",
                "assigned_to": assignee.title(),
                "priority": "High",
                "status": "Pending",
                "due": handoff.due_date or "TBD",
            })

    instructions = {}
    for agent_name, tasks in agent_tasks.items():
        if not tasks:
            continue

        lines = [
            "---",
            f"date: \"{meeting_date}\"",
            "author: \"Meeting Engine\"",
            "model: \"grok-4\"",
            "version: \"v1.0\"",
            "status: \"Active\"",
            "---\n",
            f"# {agent_name.title()} — Operational Tasks",
            f"**Source:** Daily Briefing {meeting_date}",
            "",
            "## Action Items",
            "",
            "| Task | Assigned To | Priority | Status | Due |",
            "|------|-------------|----------|--------|-----|",
        ]
        for t in tasks:
            lines.append(
                f"| {t['task']} | {t['assigned_to']} | {t['priority']} "
                f"| {t['status']} | {t['due']} |"
            )
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

        # Phase 0: Load nervous system — MUST be first (before MeetingEngine runs)
        ns_injector = NervousSystemInjector()
        await ns_injector.load()
        logger.info(
            f"Nervous system loaded for daily_briefing "
            f"({ns_injector.node_count} nodes)"
        )

        engine = MeetingEngine(
            agents=agents,
            cost_tracker=cost_tracker,
            meeting_type=self.meeting_type,
            agenda=agenda,
            num_rounds=7,
            include_manager_in_rounds=True,
            round_topics=DAILY_ROUND_TOPICS,
        )

        synthesis_raw, context_updates, transcript = await engine.run()

        # Parse structured output from Grok's synthesis
        parsed = parse_synthesis(synthesis_raw)

        # Build meeting notes (transcript only — summary rendered separately at top)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        notes = f"# BPR&D Daily Briefing — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
        notes += transcript.to_markdown()

        # Build per-agent task checklists from action items and handoffs
        agent_instructions = _build_agent_instructions(
            parsed_data=parsed,
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
            context_updates=context_updates,
            cost_estimate=CostEstimate(**cost_tracker.to_dict()),
        )
