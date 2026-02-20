"""
Work Session meeting type for BPR&D meeting service.
Executes a solo work session for an agent (default: Grok) to review status,
discover backlog items, and update handoff instructions for the team.

v3.1: Full ReAct Agent Loop — Agent can read/write files (staged) before
committing everything atomically at the end. Nervous system injected as
layer 0. /reweave appended after every session.
"""

import json
import logging
from datetime import datetime

from agents.registry import RegisteredAgent
from backlog.discovery import discover_backlog, BacklogResult
from models.meeting import MeetingResponse, CostEstimate
from meetings.base import BaseMeeting
from prompts.nervous_system_injector import NervousSystemInjector
from tools import github_tool, github_tools
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

        # Determine the primary worker
        worker_name = "grok"
        if agents:
            if len(agents) > 1:
                logger.warning(
                    f"WorkSession received {len(agents)} agents ({list(agents.keys())}). "
                    f"Only '{list(agents.keys())[0]}' will execute. "
                    "Pass a single participant for work sessions."
                )
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
            logger.info(
                f"Nervous system loaded for {worker_name} work session "
                f"({ns_injector.node_count} nodes)"
            )

            # Phase 1: Context Gathering + Backlog Discovery
            context = await self._gather_context()
            backlog = await discover_backlog()

            logger.info(
                f"Backlog discovery: {len(backlog.items)} items found, "
                f"{len(backlog.top_items)} selected for processing"
            )

            # Staged changes dict — all agent file edits accumulate here before atomic commit
            staged_changes: dict[str, str] = {}
            action_log: list[str] = []

            # Phase 2: ReAct Agent Loop (tool-calling)
            parsed_output, action_log = await self._run_agent_loop(
                worker, context, backlog, cost_tracker,
                staged_changes=staged_changes,
                action_log=action_log,
                ns_injector=ns_injector,
                agent_hook=agent_hook,
                agenda=agenda,
            )

            # Phase 3: Finalization & Commit

            # Construct Session Notes
            date_str = datetime.utcnow().strftime("%B %d, %Y")
            notes = f"# Work Session: {worker_name.title()} — {date_str}\n\n"
            notes += parsed_output.get("summary", "No summary provided.")
            notes += "\n\n"

            # Backlog processing stats
            initiative_actions = parsed_output.get("initiative_actions", [])
            actions_completed = len(initiative_actions) + len(backlog.top_items)
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

            # Add Action Log (from the ReAct loop)
            notes += "### Execution Log\n\n"
            for log_entry in action_log:
                notes += f"- {log_entry}\n"
            notes += "\n"

            # Add concrete actions from JSON (if any)
            concrete_actions = parsed_output.get("concrete_actions", [])
            if concrete_actions:
                notes += "### Concrete Actions (Summary)\n\n"
                for action in concrete_actions:
                    notes += f"- {action}\n"
                notes += "\n"

            # Add the session summary to staged changes
            session_filename = f"meetings/logs/{datetime.utcnow().strftime('%Y-%m-%d-%H%M')}-{worker_name}-session.md"
            staged_changes[session_filename] = notes

            # agent_instructions JSON field is intentionally ignored here.
            # handoff.md updates must be done explicitly via the write_file tool during the session.
            # This prevents Work Sessions from overwriting Daily Briefing handoff assignments.
            agent_instructions = parsed_output.get("agent_instructions", {})
            if agent_instructions:
                logger.info(
                    f"agent_instructions present in JSON output ({list(agent_instructions.keys())}) "
                    "but suppressed — use write_file tool to update handoff.md explicitly."
                )

            # ATOMIC COMMIT
            if staged_changes:
                commit_msg = f"Work Session: {worker_name} ({len(staged_changes)} files)"
                success = await github_tool.commit_multiple_files(staged_changes, commit_msg)
                if success:
                    logger.info(f"Atomic commit successful: {len(staged_changes)} files.")
                else:
                    logger.error("Atomic commit failed.")
            else:
                logger.info("No changes to commit.")

            return MeetingResponse(
                success=True,
                meeting_id=meeting_id,
                meeting_type=self.meeting_type,
                notes=notes,
                summary=parsed_output.get("summary", ""),
                agent_instructions=parsed_output.get("agent_instructions", {}),
                cost_estimate=CostEstimate(**cost_tracker.to_dict()),
                session_path=session_filename,
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
            content = await github_tool.read_file(path)
            context_parts.append(f"## {path}\n\n{content}\n")

        return "\n---\n".join(context_parts)

    async def _run_agent_loop(
        self,
        agent: RegisteredAgent,
        context: str,
        backlog: BacklogResult,
        tracker: CostTracker,
        staged_changes: dict[str, str] | None = None,
        action_log: list[str] | None = None,
        ns_injector: NervousSystemInjector | None = None,
        agent_hook: str = "",
        agenda: str = "",
    ) -> tuple[dict, list[str]]:
        """
        ReAct agent loop: agent calls tools (read_file/write_file/list_files/done)
        via XML tags; executor dispatches up to max_turns iterations.
        Nervous system is injected as layer 0. /reweave runs as final step.
        """
        if staged_changes is None:
            staged_changes = {}
        if action_log is None:
            action_log = []

        backlog_context = await backlog.to_context_string_with_skills()
        has_backlog = len(backlog.items) > 0

        base_system_prompt = (
            f"You are {agent.persona.name}. You are performing a work session.\n\n"
        )

        # If a manual HiC directive was provided, inject it as highest priority
        if agenda:
            base_system_prompt += (
                "⚡ HiC DIRECTIVE (HIGHEST PRIORITY):\n"
                "The following instruction comes directly from Russell (Human in Command). "
                "This overrides default backlog processing. Complete this directive FIRST, "
                "then process any remaining backlog items if time/budget allows.\n\n"
                f"{agenda}\n\n"
                "---\n\n"
            )

        base_system_prompt += (
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
            "- Required keys: 'summary'\n"
            "- 'concrete_actions' (list of strings): Every action you took on backlog items.\n"
            "- 'initiative_actions' (list of strings): Self-directed actions if backlog was empty.\n"
            "- To update a handoff file, use the write_file tool directly during the session.\n"
            "  Do NOT put handoff updates in JSON output — use write_file instead.\n\n"
            "Example Output:\n"
            "```json\n"
            "{\n"
            '  "summary": "Processed 5 backlog items. Focusing team on Hive MVP.",\n'
            '  "concrete_actions": [\n'
            '    "Assigned Hive MVP greenlight to Russell with 2026-02-19 deadline",\n'
            '    "Updated quality filter handoff status from pending to in-progress",\n'
            '    "Created follow-up for Gemini: dry-run Hive poster by EOD"\n'
            "  ],\n"
            '  "initiative_actions": []\n'
            "}\n"
            "```"
        )

        initial_user_msg = (
            f"Here is the context:\n\n{context}\n\n"
            f"---\n\n{backlog_context}\n\n"
            "Begin your work session. Use tools to read/edit files. "
            "When finished, output the Final JSON Summary."
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

        # Append tool definitions so agent knows how to call tools
        system_prompt += "\n\n" + github_tools.get_tool_definitions()

        messages = [{"role": "user", "content": initial_user_msg}]

        # ReAct Loop
        max_turns = 15
        final_json_content = ""

        for turn in range(max_turns):
            logger.info(f"Turn {turn+1}/{max_turns} for {agent.persona.name}")

            # Call LLM
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

            content = response.content
            messages.append({"role": "assistant", "content": content})

            # Parse Tool Calls
            tool_calls = github_tools.parse_tool_calls(content)

            if not tool_calls:
                # No tools called. Check if it looks like the final JSON response.
                if "```json" in content or content.strip().startswith("{"):
                    final_json_content = content
                    break
                # Otherwise, prod the agent to do something or finish
                messages.append({
                    "role": "user",
                    "content": "I did not see any tool calls. If you are finished, output the JSON summary. If not, use a tool."
                })
                continue

            # Execute Tools
            tool_results = []
            is_done = False

            for tool_name, params in tool_calls:
                logger.info(f"Agent executing tool: {tool_name}")
                result = ""

                try:
                    if tool_name == "read_file":
                        path = params.get("path")
                        result = await github_tools.read_file_tool(path, staged_changes)
                        action_log.append(f"Read file: {path}")

                    elif tool_name == "write_file":
                        path = params.get("path")
                        file_content = params.get("content")
                        result = await github_tools.write_file_tool(path, file_content, staged_changes)
                        action_log.append(f"Staged write: {path}")

                    elif tool_name == "list_files":
                        path = params.get("path", ".")
                        result = await github_tools.list_files_tool(path)
                        action_log.append(f"Listed files in: {path}")

                    elif tool_name == "done":
                        is_done = True
                        result = "Session marked as done."
                        action_log.append("Agent signaled completion.")

                    else:
                        result = f"Error: Unknown tool '{tool_name}'"

                except Exception as e:
                    result = f"Error executing tool {tool_name}: {str(e)}"
                    logger.error(f"Tool execution failed: {e}")

                tool_results.append(f"Tool '{tool_name}' Output:\n{result}")

            # Feed results back to agent
            user_feedback = "\n\n".join(tool_results)
            messages.append({"role": "user", "content": user_feedback})

            if is_done:
                # Check if the last message had JSON
                if "```json" in content or content.strip().startswith("{"):
                    final_json_content = content
                break

        # If we exited loop without JSON, use last message content
        if not final_json_content:
            final_json_content = messages[-1]["content"] if messages else "{}"

        parsed = self._parse_output(final_json_content)

        # /reweave — final step of every session: stage a skill graph reflection entry
        reweave_path = (
            f"_shared/skill-graphs/bprd-core/reflections/"
            f"{datetime.utcnow().strftime('%Y-%m-%d')}-{agent.persona.name.lower()}-reweave.md"
        )
        reweave_content = (
            f"---\n"
            f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}\n"
            f"Author: {agent.persona.name} | Session: work_session\n"
            f"---\n\n"
            f"# /reweave — {agent.persona.name} Session Reflection\n\n"
            f"## Actions Taken\n\n"
            + "\n".join(f"- {a}" for a in action_log)
            + "\n\n## Summary\n\n"
            + parsed.get("summary", "No summary captured.")
            + "\n\n"
            f"*Auto-generated by work_session /reweave. "
            f"Nervous system nodes at session start: "
            f"{ns_injector.node_count if ns_injector else 'N/A'}*\n"
        )
        staged_changes[reweave_path] = reweave_content
        action_log.append(f"/reweave staged: {reweave_path}")
        logger.info(f"/reweave entry staged: {reweave_path}")

        return parsed, action_log

    def _parse_output(self, content: str) -> dict:
        """Parse JSON from agent response."""
        # Clean markdown code blocks
        cleaned = content.strip()

        # Sometimes the agent puts text before the json
        json_start = cleaned.find("```json")
        if json_start != -1:
            cleaned = cleaned[json_start+7:]
            json_end = cleaned.find("```")
            if json_end != -1:
                cleaned = cleaned[:json_end]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

        # Or look for first { and last }
        if "{" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            cleaned = cleaned[start:end]

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
