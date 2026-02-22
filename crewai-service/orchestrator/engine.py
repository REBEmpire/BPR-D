"""
Meeting Engine for BPR&D.
Phase-driven state machine that orchestrates multi-agent dialogue
with full conversation history.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Awaitable

from agents.registry import RegisteredAgent
from llm.base import LLMResponse
from orchestrator.transcript import Transcript
from prompts.nervous_system_injector import NervousSystemInjector
from tools.github_tool import list_commits, read_file, list_sessions
# NOTE: list_handoffs removed - old handoff system deprecated in favor of BPR&D_To_Do_List v2
from tools.memory_tool import read_memory
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


@dataclass
class MeetingContext:
    """All context gathered before the meeting starts."""
    recent_commits: str = ""
    team_state: str = ""
    # NOTE: active_handoffs removed - old handoff system deprecated in favor of BPR&D_To_Do_List v2
    recent_sessions: str = ""
    protocols: str = ""
    user_context: str = ""
    agent_contexts: dict[str, str] = field(default_factory=dict)
    agenda: str = ""

    def as_summary(self) -> str:
        """Render context as a text block for agent prompts."""
        parts = []
        if self.agenda:
            parts.append(
                f"## ⚡ HiC Directive\n"
                f"> Direct instruction from Russell (Human in Command). "
                f"Treat as highest priority above all other backlog items.\n\n"
                f"{self.agenda}"
            )
        if self.team_state:
            parts.append(f"## Team State\n{self.team_state}")
        if self.recent_sessions:
            parts.append(f"## Recent Session Summaries\n{self.recent_sessions}")
        if self.recent_commits:
            parts.append(f"## Recent Commits\n{self.recent_commits}")
        # NOTE: active_handoffs section removed - see BPR&D_To_Do_List v2
        if self.protocols:
            parts.append(f"## Active Protocols\n{self.protocols}")
        if self.user_context:
            parts.append(f"## User Memory\n{self.user_context}")

        # Agent specific contexts are usually injected separately, but adding summary here
        if self.agent_contexts:
            parts.append("## Agent Contexts (active.md)")
            for agent, content in self.agent_contexts.items():
                parts.append(f"\n### {agent.upper()}\n{content}")

        return "\n\n".join(parts)


class MeetingEngine:
    """
    Core engine that drives a meeting through its phases.
    Decoupled from specific meeting types (DailyBriefing, etc) which just configure it.
    """

    def __init__(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        meeting_type: str,
        agenda: str,
        num_rounds: int = 1,
        include_manager_in_rounds: bool = True,
        round_topics: list[str] = None,
        timeout_seconds: int = 300,
    ):
        self.agents = agents
        self.cost_tracker = cost_tracker
        self.meeting_type = meeting_type
        self.agenda = agenda
        self.num_rounds = num_rounds
        self.include_manager_in_rounds = include_manager_in_rounds
        self.round_topics = round_topics or []
        self.timeout_seconds = timeout_seconds

        self.transcript = Transcript()
        self.context = MeetingContext(agenda=agenda)

        # Nervous System
        self._ns_injector = NervousSystemInjector()
        self._ns_agent_hooks = {}  # Store retrieved hooks per agent

    async def gather_context(self) -> None:
        """Phase 0: Load nervous system + gather context from GitHub, memory, and handoffs."""
        logger.info("Phase: GATHER_CONTEXT")

        # 1. Load Nervous System (load core context + agent hooks in parallel)
        await self._ns_injector.load()
        agent_names = list(self.agents.keys())
        agent_hooks = await asyncio.gather(
            *[self._ns_injector.load_agent_hook(name) for name in agent_names],
            return_exceptions=True
        )
        for name, hook in zip(agent_names, agent_hooks):
            self._ns_agent_hooks[name] = hook if isinstance(hook, str) else ""

        # 2. Gather Project State (Parallel)
        async def fetch_commits():
            try:
                return await list_commits(count=5)
            except Exception as e:
                logger.warning(f"Failed to fetch commits: {e}")
                return "Error fetching commits."

        async def fetch_team_state():
            try:
                return await read_file("_agents/team_state.md")
            except Exception:
                return ""

        # NOTE: fetch_handoffs removed - old handoff system deprecated in favor of BPR&D_To_Do_List v2

        async def fetch_sessions():
            try:
                return await list_sessions(limit=3)
            except Exception:
                return ""

        async def fetch_protocol():
            try:
                return await read_file("team_meeting_protocol_v2.md")
            except Exception:
                return ""

        async def fetch_agent_context(agent_name):
            try:
                return await read_file(f"_agents/{agent_name}/active.md")
            except Exception:
                return ""

        # Execute gathers
        results = await asyncio.gather(
            fetch_commits(),
            fetch_team_state(),
            # NOTE: fetch_handoffs() removed - see BPR&D_To_Do_List v2
            fetch_sessions(),
            fetch_protocol(),
            *[fetch_agent_context(a) for a in self.agents],
            return_exceptions=True
        )

        # Unpack results
        self.context.recent_commits = str(results[0])
        self.context.team_state = str(results[1])
        # NOTE: active_handoffs removed - see BPR&D_To_Do_List v2
        self.context.recent_sessions = str(results[2])
        self.context.protocols = str(results[3])

        agent_results = results[4:]
        for i, agent_name in enumerate(self.agents):
            if isinstance(agent_results[i], str):
                self.context.agent_contexts[agent_name] = agent_results[i]

    async def _call_agent(
        self,
        agent_name: str,
        phase: str,
        instructions: str,
        on_turn: Callable[[str, str], Awaitable[None]] = None
    ) -> LLMResponse | None:
        """Helper to call a single agent and update transcript."""
        agent = self.agents.get(agent_name)
        if not agent:
            logger.error(f"Agent {agent_name} not found!")
            return None

        # Inject Nervous System context
        agent_hook = self._ns_agent_hooks.get(agent_name, "")
        ns_preamble = self._ns_injector.inject(
            agent_name=agent_name,
            session_type=self.meeting_type,
            base_prompt="",
            model_id=getattr(agent.provider, "model", ""),
            agent_hook=agent_hook,
        )

        # Build system prompt with RICH context
        system_prompt = agent.persona.build_system_prompt(
            meeting_context=self.context.as_summary(),
            phase_instructions=instructions,
            nervous_system_preamble=ns_preamble,
        )

        # Get conversation history (excluding self to maintain flow)
        messages = self.transcript.to_messages(exclude_agent=agent_name)

        try:
            response = await agent.provider.chat(
                messages=messages,
                system=system_prompt,
                temperature=0.7,
            )

            # Record cost
            self.cost_tracker.record_usage(
                agent_name=agent_name,
                prompt_tokens=response.input_tokens,
                completion_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
            )

            # Update transcript
            self.transcript.add_turn(agent_name, phase, response.content)
            logger.info(f"  {agent_name} ({phase}): {response.output_tokens} tokens, ${response.cost_usd:.4f}")

            if on_turn:
                await on_turn(agent_name, response.content)

            return response

        except Exception as e:
            logger.error(f"Agent {agent_name} call failed: {e}", exc_info=True)
            return None

    async def grok_opens(self, on_turn: Callable = None) -> None:
        """Phase 2: Grok sets the stage."""
        logger.info("Phase: GROK_OPENS")
        instructions = (
            "You are the Chair. Open this meeting. \n"
            "1. Review the agenda/goal.\n"
            "2. Set the tone (professional but high-energy).\n"
            "3. Call on the first agent to speak."
        )
        await self._call_agent("grok", "opening", instructions, on_turn)

    async def agent_round(self, round_num: int, on_turn: Callable = None) -> None:
        """Phase 3: Round of contributions."""
        logger.info(f"Phase: ROUND_{round_num}")

        topic = "General Discussion"
        if self.round_topics and round_num <= len(self.round_topics):
            topic = self.round_topics[round_num - 1]

        logger.info(f"  Topic: {topic}")

        # Determine order
        agents_to_run = list(self.agents.keys())
        # If manager is excluded from rounds, remove grok
        if not self.include_manager_in_rounds and "grok" in agents_to_run:
            agents_to_run.remove("grok")

        for agent_name in agents_to_run:
            if agent_name == "grok":
                 # Grok specific instructions if he is in the round
                instructions = (
                    f"Round {round_num} Topic: {topic}\n"
                    "As Chair, guide the discussion or add your specific insight. "
                    "Keep it moving."
                )
            else:
                instructions = (
                    f"Round {round_num} Topic: {topic}\n"
                    "Provide your update or perspective. Be concise. "
                    "Reference specific files or data if possible."
                )

            await self._call_agent(agent_name, f"round_{round_num}", instructions, on_turn)

            if not self.cost_tracker.check_budget():
                break

    async def debate(self, on_turn: Callable = None) -> None:
        """Phase 4: Debate / Refinement (Grok led)."""
        logger.info("Phase: DEBATE")

        # Grok decides if debate is needed
        instructions = (
            "Review the discussion so far. Is there a conflict, a weak point, "
            "or a missing perspective? \n"
            "If YES: Identify it and ask a specific agent to address it. \n"
            "If NO: output 'Move to synthesis'."
            "Remember: let it get spicy. This is where ideas sharpen."
        )
        response = await self._call_agent("grok", "debate_setup", instructions, on_turn)

        if response and "move to synthesis" not in response.content.lower() and "no debate" not in response.content.lower():
            # There's a debate topic — let agents respond
            speakers = [name for name in self.agents if name != "grok"]
            for agent_name in speakers:
                debate_instructions = (
                    "Grok has identified a topic for debate. Respond to the specific points raised. "
                    "Defend your position with evidence and reasoning. Push back if you disagree. "
                    "This is where iron sharpens iron. Be direct."
                )
                await self._call_agent(agent_name, "debate", debate_instructions, on_turn)

                if not self.cost_tracker.check_budget():
                    break

    async def grok_synthesizes(self, on_turn: Callable = None) -> str:
        """Phase 5: Grok synthesizes the meeting into structured output."""
        logger.info("Phase: GROK_SYNTHESIZES")

        # NOTE: handoffs section removed from JSON output - old handoff system deprecated
        # Tasks now go to BPR&D_To_Do_List v2 via action_items
        instructions = (
            "Synthesize the entire meeting discussion into a structured summary.\n\n"
            "You MUST respond with valid JSON in exactly this format:\n"
            "```json\n"
            "{\n"
            '  "meeting_notes": "Full markdown narrative of the meeting (include key quotes, decisions, and the arc of discussion)",\n'
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
            "Be decisive. Assign clear owners and deadlines.\n"
            "NOTE: All tasks should be captured as action_items - they will be routed to BPR&D_To_Do_List."
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

            if on_turn:
                await on_turn("grok", response.content, is_synthesis=True)

            return response.content

        except Exception as e:
            logger.error(f"Grok synthesis failed: {e}", exc_info=True)
            return ""

    async def _get_agent_context_update(self, agent_name: str, instructions: str) -> str:
        """Get an agent's context update without adding it to the public transcript."""
        agent = self.agents.get(agent_name)
        if not agent:
            return ""

        # Use same context setup as _call_agent
        agent_hook = self._ns_agent_hooks.get(agent_name, "")
        ns_preamble = self._ns_injector.inject(
            agent_name=agent_name,
            session_type=self.meeting_type,
            base_prompt="",
            model_id=getattr(agent.provider, "model", ""),
            agent_hook=agent_hook,
        )

        system_prompt = agent.persona.build_system_prompt(
            meeting_context=self.context.as_summary(),
            phase_instructions=instructions,
            nervous_system_preamble=ns_preamble,
        )

        messages = self.transcript.to_messages(exclude_agent=agent_name)

        try:
            response = await agent.provider.chat(
                messages=messages,
                system=system_prompt,
                temperature=0.2, # Low temp for file generation
            )

            self.cost_tracker.record_usage(
                agent_name=agent_name,
                prompt_tokens=response.input_tokens,
                completion_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
            )

            logger.info(f"  {agent_name} (context update): {response.output_tokens} tokens")
            return response.content
        except Exception as e:
            logger.error(f"Error getting context update for {agent_name}: {e}")
            return ""

    async def context_update_round(self) -> dict[str, str]:
        """Phase 5.5: All agents update their active.md context."""
        logger.info("Phase: CONTEXT_UPDATE_ROUND")
        updates = {}

        # Iterate over ALL agents (including grok)
        for agent_name in self.agents:
            instructions = (
                "The meeting has concluded. Based on the discussion and the synthesis above, "
                "output the FULL content of your updated active.md file. "
                "Ensure you capture all new tasks, status changes, and insights. "
                "Output ONLY the markdown content, starting with the YAML frontmatter "
                "(enclosed in markdown code blocks or just raw text if you prefer, but be clean)."
            )

            content = await self._get_agent_context_update(agent_name, instructions)
            if content:
                updates[agent_name] = content

        return updates

    async def grok_closes(self, on_turn: Callable = None) -> None:
        """Phase 6: Grok delivers a memorable closing."""
        logger.info("Phase: GROK_CLOSES")

        instructions = (
            "Close this meeting with something memorable. Different every time. "
            "Motivating without being cliche. Could be a callback to the discussion, "
            "a challenge for tomorrow, a moment of real talk, or something unexpected.\n\n"
            "Keep it short (2-3 sentences max). Make it land."
        )
        await self._call_agent("grok", "closing", instructions, on_turn)

    async def run(self) -> tuple[str, dict[str, str], Transcript]:
        """Execute the full meeting flow. Returns (synthesis_output, transcript)."""
        logger.info(f"=== Starting {self.meeting_type} meeting ===")

        try:
            # Phase 1: Gather context
            await asyncio.wait_for(
                self.gather_context(),
                timeout=self.timeout_seconds,
            )

            # Phase 2: Grok opens
            await self.grok_opens()
            if not self.cost_tracker.check_budget():
                return await self._emergency_close()

            # Phase 3: Agent rounds (7 for daily briefing, 4 for fire team)
            for round_num in range(1, self.num_rounds + 1):
                await self.agent_round(round_num=round_num)
                if not self.cost_tracker.check_budget():
                    return await self._emergency_close()

            # Phase 4: Debate (Grok decides if needed)
            await self.debate()
            if not self.cost_tracker.check_budget():
                return await self._emergency_close()

            # Phase 5: Grok synthesizes
            synthesis = await self.grok_synthesizes()
            if not self.cost_tracker.check_budget():
                return synthesis, {}, self.transcript

            # Phase 5.5: Context update round
            context_updates = await self.context_update_round()

            # Phase 6: Grok closes
            await self.grok_closes()

            logger.info(f"=== Meeting complete: {len(self.transcript)} turns ===")
            return synthesis, context_updates, self.transcript

        except asyncio.TimeoutError:
            logger.error("Meeting timed out during context gathering")
            self.cost_tracker.terminated_early = True
            self.cost_tracker.termination_reason = "Context gathering timeout"
            return "", {}, self.transcript

        except Exception as e:
            logger.error(f"Meeting failed: {e}", exc_info=True)
            self.cost_tracker.terminated_early = True
            self.cost_tracker.termination_reason = str(e)
            return "", {}, self.transcript

    async def _emergency_close(self, on_turn: Callable = None) -> tuple[str, dict[str, str], Transcript]:
        """Quick close when budget is exceeded mid-meeting."""
        logger.warning("Emergency close: budget exceeded")
        self.transcript.add_turn(
            "system", "emergency",
            "[Meeting terminated early due to budget cap. "
            "Partial discussion preserved above.]"
        )
        if on_turn:
            await on_turn("system", "[Meeting terminated early due to budget cap.]")

        # Try a quick synthesis with what we have
        synthesis = await self.grok_synthesizes(on_turn)
        return synthesis, {}, self.transcript

    async def stream_events(self):
        """Execute the meeting and yield events for SSE streaming."""
        logger.info(f"=== Starting {self.meeting_type} meeting (STREAMING) ===")

        # Initialize log file
        try:
            os.makedirs("meetings/logs", exist_ok=True)
            log_path = f"meetings/logs/meeting_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.cost_tracker.meeting_id}.md"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"# Meeting Log: {self.meeting_type}\nDate: {datetime.utcnow()}\n\n")
        except Exception as e:
            logger.error(f"Failed to create log file: {e}")
            log_path = None

        # Callbacks
        async def yield_event(event_type: str, data: dict):
            payload = {"type": event_type, "timestamp": datetime.utcnow().isoformat(), **data}

            # Persist to disk immediately
            if log_path:
                try:
                    with open(log_path, "a", encoding="utf-8") as f:
                        if event_type == "turn":
                            f.write(f"\n### {data.get('agent', 'SYSTEM').upper()}\n\n{data.get('content', '')}\n\n")
                        elif event_type == "synthesis":
                             f.write(f"\n# SYNTHESIS\n\n{data.get('content', '')}\n\n")
                except Exception as e:
                    logger.error(f"Failed to append to log file: {e}")

            yield payload

        async def on_turn(agent_name: str, content: str, is_synthesis: bool = False):
            event_type = "synthesis" if is_synthesis else "turn"
            async for event in yield_event(event_type, {"agent": agent_name, "content": content}):
                yield event

        # Main Flow
        try:
            yield {"type": "start", "meeting_id": self.cost_tracker.meeting_id}

            # Phase 1: Gather context
            yield {"type": "phase", "phase": "gather_context"}
            try:
                await asyncio.wait_for(self.gather_context(), timeout=self.timeout_seconds)
            except Exception as e:
                logger.error(f"Context gathering failed: {e}")

            # Phase 2: Grok opens
            yield {"type": "phase", "phase": "grok_opens"}
            await self.grok_opens(on_turn=on_turn)

            if not self.cost_tracker.check_budget():
                await self._emergency_close(on_turn=on_turn)
                yield {"type": "complete", "status": "partial"}
                return

            # Phase 3: Agent rounds
            for round_num in range(1, self.num_rounds + 1):
                yield {"type": "phase", "phase": f"round_{round_num}"}
                await self.agent_round(round_num, on_turn=on_turn)

                if not self.cost_tracker.check_budget():
                    await self._emergency_close(on_turn=on_turn)
                    yield {"type": "complete", "status": "partial"}
                    return

            # Phase 4: Debate
            yield {"type": "phase", "phase": "debate"}
            await self.debate(on_turn=on_turn)

            if not self.cost_tracker.check_budget():
                await self._emergency_close(on_turn=on_turn)
                yield {"type": "complete", "status": "partial"}
                return

            # Phase 5: Synthesis
            yield {"type": "phase", "phase": "synthesis"}
            synthesis = await self.grok_synthesizes(on_turn=on_turn)

            # Phase 5.5: Context Updates
            yield {"type": "phase", "phase": "context_updates"}
            context_updates = await self.context_update_round()
            yield {"type": "context_updates", "updates": context_updates}

            # Phase 6: Closing
            yield {"type": "phase", "phase": "closing"}
            await self.grok_closes(on_turn=on_turn)

            yield {"type": "complete", "log_url": log_path}

        except Exception as e:
            logger.error(f"Streaming meeting failed: {e}", exc_info=True)
            yield {"type": "error", "error": str(e)}
