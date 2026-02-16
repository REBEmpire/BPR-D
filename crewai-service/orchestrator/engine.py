"""
Meeting engine for BPR&D meeting service.
Phase-driven state machine that orchestrates multi-agent dialogue
with full conversation history.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime

from agents.registry import RegisteredAgent
from llm.base import LLMResponse
from orchestrator.transcript import Transcript
from tools import list_commits, read_file, list_handoffs
from tools.memory_tool import read_memory
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


@dataclass
class MeetingContext:
    """All context gathered before the meeting starts."""
    recent_commits: str = ""
    team_state: str = ""
    active_handoffs: str = ""
    protocols: str = ""
    user_context: str = ""
    agent_contexts: dict[str, str] = field(default_factory=dict)
    agenda: str = ""

    def as_summary(self) -> str:
        """Render context as a text block for agent prompts."""
        parts = []
        if self.agenda:
            parts.append(f"## Agenda\n{self.agenda}")
        if self.team_state:
            parts.append(f"## Team State\n{self.team_state}")
        if self.recent_commits:
            parts.append(f"## Recent Commits\n{self.recent_commits}")
        if self.active_handoffs:
            parts.append(f"## Active Handoffs\n{self.active_handoffs}")
        for agent, ctx in self.agent_contexts.items():
            if ctx and not ctx.startswith("Memory file not found"):
                parts.append(f"## {agent.title()}'s Active Context\n{ctx}")
        return "\n\n".join(parts)


class MeetingEngine:
    """Orchestrates a meeting as a phase-driven state machine.

    Each phase calls specific agents with the full conversation transcript,
    enabling natural multi-turn dialogue where agents reference each other.
    """

    def __init__(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        meeting_type: str = "daily_briefing",
        agenda: str = "",
        timeout_seconds: int = 900,
    ):
        self.agents = agents
        self.cost_tracker = cost_tracker
        self.meeting_type = meeting_type
        self.agenda = agenda
        self.timeout_seconds = timeout_seconds
        self.transcript = Transcript()
        self.context = MeetingContext(agenda=agenda)

    async def _call_agent(self, agent_name: str, phase: str, instructions: str) -> LLMResponse | None:
        """Call an agent's LLM with the full transcript and instructions.

        Returns None if budget exceeded or agent not available.
        """
        if not self.cost_tracker.check_budget():
            logger.warning(f"Budget exceeded, skipping {agent_name} in {phase}")
            return None

        agent = self.agents.get(agent_name)
        if not agent:
            logger.warning(f"Agent {agent_name} not available")
            return None

        system_prompt = agent.persona.build_system_prompt(
            meeting_context=self.context.as_summary(),
            phase_instructions=instructions,
        )

        # Build messages from transcript (this agent's turns as 'assistant', others as 'user')
        messages = self.transcript.to_messages(exclude_agent=agent_name)

        # If no messages yet (first turn), add a starter
        if not messages:
            messages = [{"role": "user", "content": f"Meeting type: {self.meeting_type}. Begin."}]

        try:
            response = await agent.provider.chat(
                messages=messages,
                system=system_prompt,
                temperature=agent.persona.temperature,
            )

            # Record costs
            self.cost_tracker.record_usage(
                agent_name=agent_name,
                prompt_tokens=response.input_tokens,
                completion_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
            )

            # Add to transcript
            self.transcript.add_turn(agent_name, phase, response.content)

            logger.info(
                f"  {agent_name} ({phase}): {response.output_tokens} tokens, "
                f"${response.cost_usd:.4f}"
            )

            return response

        except Exception as e:
            logger.error(f"Error calling {agent_name}: {e}", exc_info=True)
            self.transcript.add_turn(
                agent_name, phase,
                f"[{agent_name} encountered an error and could not respond: {e}]"
            )
            return None

    async def gather_context(self) -> None:
        """Phase 1: Gather context from GitHub, memory, and handoffs."""
        logger.info("Phase: CONTEXT_GATHERING")

        # Fetch context in parallel
        results = await asyncio.gather(
            list_commits(count=10),
            read_memory("shared", "team_state"),
            list_handoffs(),
            read_memory("shared", "protocols"),
            read_memory("shared", "user_context"),
            return_exceptions=True,
        )

        self.context.recent_commits = results[0] if isinstance(results[0], str) else ""
        self.context.team_state = results[1] if isinstance(results[1], str) else ""
        self.context.active_handoffs = results[2] if isinstance(results[2], str) else ""
        self.context.protocols = results[3] if isinstance(results[3], str) else ""
        self.context.user_context = results[4] if isinstance(results[4], str) else ""

        # Load each agent's active context
        agent_ctx_tasks = []
        for name in self.agents:
            agent_ctx_tasks.append(read_memory(name, "context"))
        agent_contexts = await asyncio.gather(*agent_ctx_tasks, return_exceptions=True)
        for name, ctx in zip(self.agents.keys(), agent_contexts):
            self.context.agent_contexts[name] = ctx if isinstance(ctx, str) else ""

        logger.info("Context gathered successfully")

    async def grok_opens(self) -> None:
        """Phase 2: Grok opens the meeting."""
        logger.info("Phase: GROK_OPENS")

        today = datetime.utcnow().strftime("%A, %B %d, %Y")
        instructions = (
            f"Open today's {self.meeting_type.replace('_', ' ')} meeting ({today}).\n\n"
            "CRITICAL: Open DIFFERENTLY EVERY TIME. A question, a challenge, a piece of news, "
            "silence, mid-thought, a callback to a past meeting. NEVER predictable. "
            "NEVER 'Good morning team'.\n\n"
            "After your opening, review the context provided and present a meeting agenda "
            "with 3-5 prioritized topics. For each topic, note:\n"
            "- What it is\n"
            "- Why it matters now\n"
            "- Which agents should weigh in\n\n"
            "Keep it sharp and direct. Set the tone for the entire meeting."
        )
        await self._call_agent("grok", "opening", instructions)

    async def agent_round(self, round_num: int = 1) -> None:
        """Phase 3: Each non-manager agent provides their perspective."""
        logger.info(f"Phase: AGENT_ROUND_{round_num}")

        # Determine speaking order (everyone except grok)
        speakers = [name for name in self.agents if name != "grok"]

        for agent_name in speakers:
            instructions = (
                f"Review the full conversation so far and provide your perspective "
                f"(Round {round_num}).\n\n"
                "For each agenda topic that's relevant to your expertise:\n"
                "- Share your analysis or insights\n"
                "- Explicitly reference other agents' points (agree, disagree, build on)\n"
                "- Ask one sharp question if something's unclear\n"
                "- Propose concrete next steps from your domain\n\n"
                "Also report on any pending handoffs or work assigned to you.\n\n"
                "Stay in character. Be substantive. Reference what others actually said."
            )
            await self._call_agent(agent_name, f"round_{round_num}", instructions)

            if not self.cost_tracker.check_budget():
                break

    async def debate(self) -> None:
        """Phase 4 (optional): Targeted exchanges on contentious points."""
        logger.info("Phase: DEBATE")

        # Ask Grok to identify debate-worthy topics
        instructions = (
            "Based on the discussion so far, are there any points of genuine disagreement "
            "or tension that would benefit from deeper debate? If so, identify them and "
            "call on specific agents to defend their positions. If not, say so briefly "
            "and move to synthesis.\n\n"
            "Remember: let it get spicy. This is where ideas sharpen."
        )
        response = await self._call_agent("grok", "debate_setup", instructions)

        if response and "move to synthesis" not in response.content.lower() and "no debate" not in response.content.lower():
            # There's a debate topic — let agents respond
            speakers = [name for name in self.agents if name != "grok"]
            for agent_name in speakers:
                debate_instructions = (
                    "Grok has identified a topic for debate. Respond to the specific points raised. "
                    "Defend your position with evidence and reasoning. Push back if you disagree. "
                    "This is where iron sharpens iron. Be direct."
                )
                await self._call_agent(agent_name, "debate", debate_instructions)

                if not self.cost_tracker.check_budget():
                    break

    async def grok_synthesizes(self) -> str:
        """Phase 5: Grok synthesizes the meeting into structured output."""
        logger.info("Phase: GROK_SYNTHESIZES")

        instructions = (
            "Synthesize the entire meeting discussion into a structured summary.\n\n"
            "You MUST respond with valid JSON in exactly this format:\n"
            "```json\n"
            "{\n"
            '  "meeting_notes": "Full markdown narrative of the meeting (include key quotes, decisions, and the arc of discussion)",\n'
            '  "handoffs": [\n'
            "    {\n"
            '      "task_id": "handoff-descriptive-name-YYYYMMDD",\n'
            '      "assigned_to": "agent_name or russell",\n'
            '      "title": "Clear task title",\n'
            '      "due_date": "YYYY-MM-DD",\n'
            '      "priority": "low|medium|high|critical",\n'
            '      "context": "Why this task exists",\n'
            '      "acceptance_criteria": ["criterion 1", "criterion 2"],\n'
            '      "status": "open",\n'
            '      "created_by": "grok"\n'
            "    }\n"
            "  ],\n"
            '  "action_items": [\n'
            "    {\n"
            '      "task": "What needs to be done",\n'
            '      "assigned_to": "who",\n'
            '      "priority": "low|medium|high|critical",\n'
            '      "deadline": "YYYY-MM-DD or null"\n'
            "    }\n"
            "  ],\n"
            '  "key_decisions": ["Decision 1 with rationale", "Decision 2 with rationale"],\n'
            '  "for_russell": "Items requiring human input or decision"\n'
            "}\n"
            "```\n\n"
            "Include a 'For Russell' section in meeting_notes highlighting items needing human input.\n"
            "Be decisive. Assign clear owners and deadlines."
        )

        # For synthesis, use the raw transcript so Grok sees everything as context
        agent = self.agents.get("grok")
        if not agent:
            return ""

        system_prompt = agent.persona.build_system_prompt(
            meeting_context=self.context.as_summary(),
            phase_instructions=instructions,
        )

        messages = self.transcript.to_raw_messages()
        if not messages:
            messages = [{"role": "user", "content": "No discussion occurred."}]

        try:
            response = await agent.provider.chat(
                messages=messages,
                system=system_prompt,
                temperature=0.5,  # Lower temp for structured output
            )

            self.cost_tracker.record_usage(
                agent_name="grok",
                prompt_tokens=response.input_tokens,
                completion_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
            )

            self.transcript.add_turn("grok", "synthesis", response.content)
            logger.info(f"  grok (synthesis): {response.output_tokens} tokens, ${response.cost_usd:.4f}")

            return response.content

        except Exception as e:
            logger.error(f"Grok synthesis failed: {e}", exc_info=True)
            return ""

    async def grok_closes(self) -> None:
        """Phase 6: Grok delivers a memorable closing."""
        logger.info("Phase: GROK_CLOSES")

        instructions = (
            "Close this meeting with something memorable. Different every time. "
            "Motivating without being cliche. Could be a callback to the discussion, "
            "a challenge for tomorrow, a moment of real talk, or something unexpected.\n\n"
            "Keep it short (2-3 sentences max). Make it land."
        )
        await self._call_agent("grok", "closing", instructions)

    async def run(self) -> tuple[str, Transcript]:
        """Execute the full meeting flow. Returns (synthesis_output, transcript)."""
        logger.info(f"=== Starting {self.meeting_type} meeting ===")

        try:
            # Phase 1: Gather context
            await asyncio.wait_for(
                self.gather_context(),
                timeout=30,
            )

            # Phase 2: Grok opens
            await self.grok_opens()
            if not self.cost_tracker.check_budget():
                return await self._emergency_close()

            # Phase 3: Agent round
            await self.agent_round(round_num=1)
            if not self.cost_tracker.check_budget():
                return await self._emergency_close()

            # Phase 4: Debate (Grok decides if needed)
            await self.debate()
            if not self.cost_tracker.check_budget():
                return await self._emergency_close()

            # Phase 5: Grok synthesizes
            synthesis = await self.grok_synthesizes()
            if not self.cost_tracker.check_budget():
                return synthesis, self.transcript

            # Phase 6: Grok closes
            await self.grok_closes()

            logger.info(f"=== Meeting complete: {len(self.transcript)} turns ===")
            return synthesis, self.transcript

        except asyncio.TimeoutError:
            logger.error("Meeting timed out during context gathering")
            self.cost_tracker.terminated_early = True
            self.cost_tracker.termination_reason = "Context gathering timeout"
            return "", self.transcript

        except Exception as e:
            logger.error(f"Meeting failed: {e}", exc_info=True)
            self.cost_tracker.terminated_early = True
            self.cost_tracker.termination_reason = str(e)
            return "", self.transcript

    async def _emergency_close(self) -> tuple[str, Transcript]:
        """Quick close when budget is exceeded mid-meeting."""
        logger.warning("Emergency close: budget exceeded")
        self.transcript.add_turn(
            "system", "emergency",
            "[Meeting terminated early due to budget cap. "
            "Partial discussion preserved above.]"
        )
        # Try a quick synthesis with what we have
        synthesis = await self.grok_synthesizes()
        return synthesis, self.transcript
