"""
Work Session meeting type for BPR&D meeting service.
Executes a solo work session for an agent (default: Grok) to review status,
discover backlog items, and update handoff instructions for the team.

v2.0: Backlog discovery integration — scans repo for open/pending items,
feeds them into the agent prompt, and reports processing stats.
"""

import json
import logging
from datetime import datetime

from agents.registry import RegisteredAgent
from backlog.discovery import discover_backlog, BacklogResult
from models.meeting import MeetingResponse, CostEstimate
from meetings.base import BaseMeeting
from prompts.nervous_system_injector import NervousSystemInjector
from tools.github_tool import read_file
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class WorkSession(BaseMeeting):
    meeting_type = "work_session"

    async def execute(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
    ) -> MeetingResponse:
        meeting_id = f"work_session-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        cost_tracker.meeting_id = meeting_id

        # Determine the primary worker (default to grok if not specified or multiple)
        worker_name = "grok"
        if agents:
            worker_name = list(agents.keys())[0]

        worker = agents.get(worker_name)
        if not worker:
            return MeetingResponse(
                success=False,
                meeting_id=meeting_id,
                meeting_type=self.meeting_type,
                notes="Worker agent not found",
                error=f"Agent '{worker_name}' not available.",
            )

        logger.info(f"Executing Work Session for {worker_name}: {meeting_id}")

        try:
            # Phase 0: Load nervous system — MUST be first
            ns_injector = NervousSystemInjector()
            await ns_injector.load()
            agent_hook = await ns_injector.load_agent_hook(worker_name)
            logger.info(f"Nervous system loaded for {worker_name} work session")

            # Phase 1: Context Gathering + Backlog Discovery
            context = await self._gather_context()
            backlog = await discover_backlog()

            logger.info(
                f"Backlog discovery: {len(backlog.items)} items found, "
                f"{len(backlog.top_items)} selected for processing"
            )

            # Phase 2: Execution (Prompting the Agent with backlog context + nervous system)
            response_content = await self._run_agent_execution(
                worker, context, backlog, cost_tracker,
                ns_injector=ns_injector, agent_hook=agent_hook,
            )

            # Phase 3: Parsing
            parsed = self._parse_output(response_content)

            # Count initiative actions
            initiative_actions = parsed.get("initiative_actions", [])
            actions_completed = len(initiative_actions) + len(backlog.top_items)

            # Format notes with backlog stats
            date_str = datetime.utcnow().strftime("%B %d, %Y")
            notes = f"# Work Session: {worker_name.title()} — {date_str}\n\n"
            notes += parsed.get("summary", "No summary provided.")
            notes += "\n\n"

            # Backlog processing section
            notes += "## Backlog Processing\n\n"
            notes += f"{backlog.stats_line(actions_completed=actions_completed)}\n\n"

            if backlog.top_items:
                notes += "### Items Processed\n\n"
                notes += "| Item | Source | Priority | Status |\n"
                notes += "|------|--------|----------|--------|\n"
                for item in backlog.top_items:
                    notes += (
                        f"| {item.title[:80]} | `{item.source}` | "
                        f"{item.priority} | {item.status} |\n"
                    )
                notes += "\n"
            else:
                notes += "No open backlog items — heartbeat only.\n\n"

            if initiative_actions:
                notes += "### Initiative Actions Taken\n\n"
                for action in initiative_actions:
                    notes += f"- {action}\n"
                notes += "\n"

            # Concrete actions log
            concrete_actions = parsed.get("concrete_actions", [])
            if concrete_actions:
                notes += "### Concrete Actions Log\n\n"
                for action in concrete_actions:
                    notes += f"- {action}\n"
                notes += "\n"

            return MeetingResponse(
                success=True,
                meeting_id=meeting_id,
                meeting_type=self.meeting_type,
                notes=notes,
                summary=parsed.get("summary", ""),
                agent_instructions=parsed.get("agent_instructions", {}),
                cost_estimate=CostEstimate(**cost_tracker.to_dict()),
            )

        except Exception as e:
            logger.error(f"Work Session failed: {e}", exc_info=True)
            return MeetingResponse(
                success=False,
                meeting_id=meeting_id,
                meeting_type=self.meeting_type,
                notes="",
                error=str(e),
                cost_estimate=CostEstimate(**cost_tracker.to_dict()),
            )

    async def _gather_context(self) -> str:
        """Gather context from GitHub files."""
        files_to_read = [
            "_agents/team_state.md",
            "_agents/grok/handoff.md",
            "_agents/claude/handoff.md",
            "_agents/gemini/handoff.md",
            "_agents/abacus/handoff.md",
        ]

        context_parts = []
        for path in files_to_read:
            content = await read_file(path)
            context_parts.append(f"## {path}\n\n{content}\n")

        return "\n---\n".join(context_parts)

    async def _run_agent_execution(
        self,
        agent: RegisteredAgent,
        context: str,
        backlog: BacklogResult,
        tracker: CostTracker,
        ns_injector: NervousSystemInjector | None = None,
        agent_hook: str = "",
    ) -> str:
        """Run the agent with full context including backlog items and nervous system preamble.

        The nervous system preamble is injected as the VERY FIRST content in the system prompt.
        """
        backlog_context = await backlog.to_context_string_with_skills()
        has_backlog = len(backlog.items) > 0

        base_system_prompt = (
            f"You are {agent.persona.name}. You are performing a scheduled work session.\n\n"
            "Your Goal:\n"
            "1. Review the current Team State and Handoffs.\n"
            "2. Review the BACKLOG ITEMS provided — these are real open tasks from the repo.\n"
            "   NOTE: Each backlog item includes [[Linked Skill Context]] from the skill graph.\n"
            "   Use that context to understand HOW to execute each task.\n"
            "3. For each backlog item: decide if it should be actioned now, deferred, or delegated.\n"
            "4. Generate updated 'handoff.md' instructions for each agent.\n\n"
            "BACKLOG PROCESSING (MANDATORY):\n"
        )

        if has_backlog:
            base_system_prompt += (
                "- You have been given real open backlog items from the repository.\n"
                "- Each item includes [[Linked Skill Context]] — read it to know HOW to execute.\n"
                "- For EACH item: take a concrete action (update a status, create a follow-up, "
                "assign to the right agent, mark progress, or note why it's deferred).\n"
                "- Document every action in 'concrete_actions' (list of strings).\n"
                "- Even small actions count: 'Updated status of X in handoff', "
                "'Created follow-up handoff for Abacus', 'Noted blocker on Y'.\n"
            )
        else:
            base_system_prompt += (
                "- No active backlog items were found in the repository.\n"
                "- INITIATIVE RULE: Select 3-5 tasks that will improve BPR&D in a tangible way.\n"
                "- See [[skill-initiative-rule]] in the skill graph for examples and format.\n"
                "- Examples: write a research brief, /reflect to add a skill node, audit a module.\n"
                "- Document ALL initiative actions in 'initiative_actions' (list of strings).\n"
            )

        base_system_prompt += (
            "\nCritical Instructions:\n"
            "- Review your previous handoff: Ensure NO action items are dropped unless completed.\n"
            "- Future Items: Maintain a 'Future/Backlog' section for items not immediately actionable.\n"
            "- Requests for Team: Explicitly list what you need from others in your handoff.\n"
            "- Abacus: Keep Abacus's To-Do list short and focused to avoid limiting out.\n\n"
            "Output Rules:\n"
            "- You MUST respond with valid JSON.\n"
            "- Required keys: 'summary', 'agent_instructions'\n"
            "- 'agent_instructions' maps agent_name -> markdown content (table format).\n"
            "- 'concrete_actions' (list of strings): Every action you took on backlog items.\n"
            "- 'initiative_actions' (list of strings): Self-directed actions if backlog was empty.\n\n"
            "CRITICAL FORMAT RULE for agent_instructions:\n"
            "- Agent handoff instructions MUST use markdown TABLE format, NOT checklists.\n"
            "- Use columns: Task | Assigned To | Priority | Status | Due\n"
            "- Priority values: URGENT, High, Medium, Low\n"
            "- Status values: Pending, In Progress, Blocked, Done\n\n"
            "Example Output:\n"
            "```json\n"
            "{\n"
            '  "summary": "Processed 5 backlog items. Focusing team on Hive MVP.",\n'
            '  "concrete_actions": [\n'
            '    "Assigned Hive MVP greenlight to Russell with 2026-02-19 deadline",\n'
            '    "Updated quality filter handoff status from pending to in-progress",\n'
            '    "Created follow-up for Gemini: dry-run Hive poster by EOD"\n'
            "  ],\n"
            '  "initiative_actions": [],\n'
            '  "agent_instructions": {\n'
            '    "grok": "# Instructions\\n\\n## Action Items\\n\\n| Task | Assigned To | Priority | Status | Due |\\n|------|-------------|----------|--------|-----|\\n| Validate meeting engine | Grok | URGENT | Pending | 2026-02-19 |\\n\\n## Backlog\\n\\n| Task | Assigned To | Priority | Status | Due |\\n|------|-------------|----------|--------|-----|\\n| State of Team dashboard | Grok | Low | Pending | |\\n\\n## Requests for Team\\n- Claude: Share API specs."\n'
            "  }\n"
            "}\n"
            "```"
        )

        user_message = (
            f"Here is the current context:\n\n{context}\n\n"
            f"---\n\n{backlog_context}\n\n"
            "Proceed with your work session. Process the backlog items and generate updated handoffs."
        )

        # Prepend nervous system preamble as the VERY FIRST content
        if ns_injector and ns_injector._context.loaded:
            ns_preamble = ns_injector.inject(
                agent_name=agent.persona.name.lower(),
                session_type="work_session",
                base_prompt="",
                model_id=getattr(agent.provider, "model", ""),
                agent_hook=agent_hook,
            )
            system_prompt = ns_preamble + "\n\n---\n\n" + base_system_prompt
        else:
            system_prompt = base_system_prompt

        messages = [{"role": "user", "content": user_message}]

        response = await agent.provider.chat(
            messages=messages,
            system=system_prompt,
            temperature=0.2,
        )

        tracker.record_usage(
            agent_name=agent.persona.name.lower(),
            prompt_tokens=response.input_tokens,
            completion_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
        )

        return response.content

    def _parse_output(self, content: str) -> dict:
        """Parse JSON from agent response."""
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from content: {content[:200]}...")
            return {
                "summary": "Failed to parse agent output.",
                "agent_instructions": {},
                "concrete_actions": [],
                "initiative_actions": [],
            }
