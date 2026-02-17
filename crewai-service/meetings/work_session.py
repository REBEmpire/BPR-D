"""
Work Session meeting type for BPR&D meeting service.
Executes a solo work session for an agent (default: Grok) to review status
and update handoff instructions for the team.
"""

import json
import logging
import asyncio
from datetime import datetime

from agents.registry import RegisteredAgent
from models.meeting import MeetingResponse, CostEstimate
from meetings.base import BaseMeeting
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
            # If agents are passed, pick the first one as the worker
            worker_name = list(agents.keys())[0]

        worker = agents.get(worker_name)
        if not worker:
             return MeetingResponse(
                success=False,
                meeting_id=meeting_id,
                meeting_type=self.meeting_type,
                notes="Worker agent not found",
                error=f"Agent '{worker_name}' not available."
            )

        logger.info(f"Executing Work Session for {worker_name}: {meeting_id}")

        try:
            # Phase 1: Context Gathering
            context = await self._gather_context()

            # Phase 2: Execution (Prompting the Agent)
            response_content = await self._run_agent_execution(worker, context, cost_tracker)

            # Phase 3: Parsing
            parsed = self._parse_output(response_content)

            # Format notes
            notes = f"# Work Session: {worker_name.title()} — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
            notes += parsed.get("summary", "No summary provided.")

            return MeetingResponse(
                success=True,
                meeting_id=meeting_id,
                meeting_type=self.meeting_type,
                notes=notes,
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
            # We assume read_file handles errors gracefully (returns error msg string)
            content = await read_file(path)
            context_parts.append(f"## {path}\n\n{content}\n")

        return "\n---\n".join(context_parts)

    async def _run_agent_execution(self, agent: RegisteredAgent, context: str, tracker: CostTracker) -> str:
        """Run the agent loop."""

        system_prompt = (
            f"You are {agent.persona.name}. You are performing a scheduled work session.\n"
            "Your Goal:\n"
            "1. Review the current Team State and Handoffs.\n"
            "2. Decide what needs to be done next for yourself and each team member.\n"
            "3. Generate updated 'handoff.md' instructions for each agent.\n\n"
            "Critical Instructions:\n"
            "- Review your previous handoff: Ensure NO action items are dropped unless completed.\n"
            "- Future Items: Maintain a 'Future/Backlog' section for items not immediately actionable.\n"
            "- Requests for Team: Explicitly list what you need from others in your handoff so they see it.\n"
            "- Abacus: Keep Abacus's To-Do list short and focused to avoid limiting out.\n\n"
            "Output Rules:\n"
            "- You MUST respond with valid JSON.\n"
            "- The JSON must have 'summary' and 'agent_instructions'.\n"
            "- 'agent_instructions' maps agent_name -> markdown content.\n\n"
            "Example Output:\n"
            "```json\n"
            "{\n"
            '  "summary": "Reviewed status. Focusing team on API integration.",\n'
            '  "agent_instructions": {\n'
            '    "grok": "# Instructions\\n## Action Items\\n- [ ] Review PR #123\\n\\n## Future/Backlog\\n- Refactor auth module\\n\\n## Requests for Team\\n- Claude: Need API specs.",\n'
            '    "claude": "# Instructions\\n- Refactor auth module..."\n'
            "  }\n"
            "}\n"
            "```"
        )

        user_message = f"Here is the current context:\n\n{context}\n\nProceed with your work session."

        messages = [{"role": "user", "content": user_message}]

        # Using provider.chat
        response = await agent.provider.chat(
            messages=messages,
            system=system_prompt,
            temperature=0.2, # Low temp for reliable JSON
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
        # Strip markdown code blocks if present
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
            logger.error(f"Failed to parse JSON from content: {content[:100]}...")
            # Fallback
            return {
                "summary": "Failed to parse agent output.",
                "agent_instructions": {}
            }
