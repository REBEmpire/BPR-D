"""
Fire Team Meeting (Special Session) for BPR&D meeting service.
HiC-triggered deep collaboration: 4 rounds with all agents, then final deliverables.

Phases: Context → Grok Opens → 4 Agent Rounds → Debate → Grok Synthesizes → Context Updates → Grok Closes
"""

import logging
from datetime import datetime

from agents.registry import RegisteredAgent
from models.meeting import MeetingResponse, CostEstimate
from orchestrator.engine import MeetingEngine
from output.parser import parse_synthesis
from prompts.nervous_system_injector import NervousSystemInjector
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

FIRE_TEAM_ROUND_TOPICS = [
    "Focus: Initial Analysis — Analyze the problem/task. Share your expertise, "
    "identify key challenges, and propose initial approaches.",
    "Focus: Response & Debate — Respond to what others said in Round 1. "
    "Build on ideas, challenge assumptions, refine proposals.",
    "Focus: Convergence — Identify what the team agrees on. Resolve remaining "
    "conflicts. Narrow to actionable solutions with clear owners.",
    "Focus: Final Deliverables — Deliver final recommendations and concrete "
    "outputs. If you have code, configs, or specs ready, output them now. "
    "Tag deployable code with ```ship-to-repo path=target/file.ext```.",
]


class SpecialSession:
    meeting_type = "special_session"

    async def execute(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
        num_rounds: int = 4,
    ) -> MeetingResponse:
        # Clamp rounds to 2-13 range
        num_rounds = max(2, min(13, num_rounds))

        meeting_id = f"special-session-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        cost_tracker.meeting_id = meeting_id

        logger.info(f"Executing Fire Team Meeting: {meeting_id} ({num_rounds} rounds)")

        # Load nervous system
        ns_injector = NervousSystemInjector()
        await ns_injector.load()
        logger.info(
            f"Nervous system loaded for special_session "
            f"({ns_injector.node_count} nodes)"
        )

        # Build round topics: use the 4 base topics, then generate additional
        # guidance for extra rounds beyond 4
        round_topics = list(FIRE_TEAM_ROUND_TOPICS[:num_rounds])
        if num_rounds > len(FIRE_TEAM_ROUND_TOPICS):
            for i in range(len(FIRE_TEAM_ROUND_TOPICS), num_rounds):
                round_topics.append(
                    f"Focus: Extended Discussion (Round {i + 1}) — "
                    "Continue refining deliverables, resolve open questions, "
                    "deepen analysis, and produce additional concrete outputs."
                )

        engine = MeetingEngine(
            agents=agents,
            cost_tracker=cost_tracker,
            meeting_type=self.meeting_type,
            agenda=agenda,
            num_rounds=num_rounds,
            include_manager_in_rounds=True,
            round_topics=round_topics,
        )

        synthesis_raw, context_updates, transcript = await engine.run()
        parsed = parse_synthesis(synthesis_raw)

        # Extract topic from agenda
        topic = (
            agenda.replace("**⚡ HiC Goal:** ", "").split("\n")[0]
            if agenda
            else "General Topic"
        )

        notes = f"# Fire Team Meeting: {topic}\n"
        notes += f"**Date:** {datetime.utcnow().strftime('%B %d, %Y')}\n"
        notes += f"**Triggered By:** HiC (Russell)\n"
        notes += f"**Rounds:** {num_rounds}\n"
        notes += f"**Participants:** {', '.join(agents.keys())}\n\n"
        notes += transcript.to_markdown()

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
            context_updates=context_updates,
            cost_estimate=CostEstimate(**cost_tracker.to_dict()),
        )
