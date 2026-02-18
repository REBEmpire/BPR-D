"""
Work Session meeting type for BPR&D meeting service.
Executes a solo work session for an agent (default: Grok) to review status,
discover backlog items, and update handoff instructions for the team.

v3.0: Full ReAct Agent Loop — Agent can read/write files (staged) before
committing everything atomically at the end.
"""

import json
import logging
from datetime import datetime

from agents.registry import RegisteredAgent
from backlog.discovery import discover_backlog, BacklogResult
from models.meeting import MeetingResponse, CostEstimate
from meetings.base import BaseMeeting
from tools import github_tool  # Backend API
from tools import github_tools # Agent Tools
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
            # Phase 1: Context Gathering + Backlog Discovery
            context = await self._gather_context()
            backlog = await discover_backlog()

            logger.info(
                f"Backlog discovery: {len(backlog.items)} items found, "
                f"{len(backlog.top_items)} selected for processing"
            )

            # Phase 2: Execution (ReAct Loop)
            # Initialize staged changes (virtual filesystem)
            staged_changes = {}

            # Run the agent loop
            # Returns the final JSON summary/handoffs
            parsed_output, action_log = await self._run_agent_loop(
                worker, context, backlog, cost_tracker, staged_changes
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
            session_filename = f"_agents/_sessions/{datetime.utcnow().strftime('%Y-%m-%d')}-{worker_name}-session.md"
            staged_changes[session_filename] = notes

            # Also update handoffs if they were returned in JSON (as a fallback or explicit update)
            # Note: The agent *should* have updated handoff files via `write_file` tool.
            # But if it put them in `agent_instructions` JSON, we can auto-update them too.
            agent_instructions = parsed_output.get("agent_instructions", {})
            for agent_name, content in agent_instructions.items():
                handoff_path = f"_agents/{agent_name}/handoff.md"
                # Only overwrite if not already modified by tool
                if handoff_path not in staged_changes:
                    staged_changes[handoff_path] = content
                    action_log.append(f"Updated {handoff_path} from final JSON output.")

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
            # We use the backend tool directly here as we are establishing initial context
            content = await github_tool.read_file(path)
            context_parts.append(f"## {path}\n\n{content}\n")

        return "\n---\n".join(context_parts)

    async def _run_agent_loop(
        self,
        agent: RegisteredAgent,
        context: str,
        backlog: BacklogResult,
        tracker: CostTracker,
        staged_changes: dict,
    ) -> tuple[dict, list[str]]:
        """
        Run the agent with full context and tools loop.
        Returns (parsed_json_output, action_log_list).
        """
        action_log = []
        messages = []

        backlog_context = backlog.to_context_string()
        tool_defs = github_tools.get_tool_definitions()

        system_prompt = (
            f"You are {agent.persona.name}. You are performing a scheduled work session.\n\n"
            f"{tool_defs}\n\n"
            "Your Goal:\n"
            "1. Review Team State and Handoffs.\n"
            "2. Review BACKLOG ITEMS and execute work using tools.\n"
            "3. Update your handoff and other agent handoffs as needed using `write_file`.\n"
            "4. When finished, call the `done` tool.\n\n"
            "CRITICAL: You have access to tools. USE THEM.\n"
            "- If you see a task to 'Update file X', use `read_file` then `write_file`.\n"
            "- Changes are STAGED. They are committed only when you finish.\n"
            "- Work through the backlog items concretely.\n\n"
            "OUTPUT FORMAT:\n"
            "You can intersperse thought, analysis, and tool calls.\n"
            "To use a tool, output XML: <execute_tool name=\"...\">...</execute_tool>\n\n"
            "FINAL OUTPUT (when calling `done` or finishing):\n"
            "You MUST output a final JSON summary block (just like a normal response) "
            "containing 'summary', 'agent_instructions', 'concrete_actions', 'initiative_actions'.\n"
            "This JSON should reflect the work you JUST did using the tools."
        )

        initial_user_msg = (
            f"Here is the context:\n\n{context}\n\n"
            f"---\n\n{backlog_context}\n\n"
            "Begin your work session. Use tools to read/edit files. "
            "When finished, output the Final JSON Summary."
        )

        messages.append({"role": "user", "content": initial_user_msg})

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

        # If we exited loop without JSON, try to find it in history or ask for it?
        # For simplicity, if we don't have it, we return a basic one.
        if not final_json_content:
            # Last ditch effort: ask for it? Or just parse the last message.
            final_json_content = messages[-1]["content"] if messages else "{}"

        parsed = self._parse_output(final_json_content)
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
