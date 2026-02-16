"""
Daily Morning Briefing Crew
Phase 1 proof-of-concept crew for BPR&D.

Schedule: 07:47 AM PST daily (triggered by n8n)
Duration target: <10 minutes
Process: Hierarchical (Grok manages)
Agents: Grok (manager), Claude, Gemini [+ Abacus when available]

Flow:
  1. Grok reviews repo state and crafts agenda
  2. Claude provides strategic analysis
  3. Gemini provides technical reality check
  4. Grok synthesizes, assigns action items, creates handoffs
"""

import json
import logging
from datetime import datetime

from crewai import Crew, Task, Process

from agents.grok import create_grok_agent
from agents.claude import create_claude_agent
from agents.gemini import create_gemini_agent
from tools.github_tool import GitHubListCommitsTool, GitHubReadTool, GitHubListHandoffsTool
from tools.memory_tool import AgentMemoryTool
from models.meeting import MeetingResponse, HandoffItem, ActionItem, CostEstimate

logger = logging.getLogger(__name__)


# Output schema for the final synthesis task
SYNTHESIS_OUTPUT_SCHEMA = """
Your output MUST be valid JSON with exactly this structure:
{
  "meeting_notes": "Full meeting notes as markdown string. Include dialogue, decisions, and the complete meeting narrative.",
  "handoffs": [
    {
      "task_id": "handoff-descriptive-name-YYYYMMDD",
      "assigned_to": "agent_name or russell",
      "title": "Clear task title",
      "due_date": "YYYY-MM-DD",
      "priority": "low|medium|high|critical",
      "context": "Why this task exists",
      "acceptance_criteria": ["criterion 1", "criterion 2"],
      "dependencies": [],
      "status": "open",
      "created_by": "grok"
    }
  ],
  "action_items": [
    {
      "task": "What needs to be done",
      "assigned_to": "who",
      "priority": "low|medium|high|critical",
      "deadline": "YYYY-MM-DD or null"
    }
  ],
  "key_decisions": ["Decision 1 with rationale", "Decision 2 with rationale"]
}
"""


def create_daily_briefing_crew(
    agenda: str | None = None,
    include_abacus: bool = False,
) -> tuple[Crew, dict]:
    """
    Create the Daily Morning Briefing crew.

    Args:
        agenda: Optional focus topic. If None, uses general daily sync.
        include_abacus: Whether to include Abacus (default False until Feb 23).

    Returns:
        Tuple of (crew, metadata) where metadata includes agent references.
    """

    # --- Tools ---
    github_commits = GitHubListCommitsTool()
    github_read = GitHubReadTool()
    github_handoffs = GitHubListHandoffsTool()
    memory = AgentMemoryTool()

    manager_tools = [github_commits, github_read, github_handoffs, memory]
    analyst_tools = [github_read, memory]

    # --- Agents ---
    grok = create_grok_agent(tools=manager_tools)
    claude = create_claude_agent(tools=analyst_tools)
    gemini = create_gemini_agent(tools=analyst_tools)

    agents = [grok, claude, gemini]

    if include_abacus:
        from agents.abacus import create_abacus_agent
        abacus = create_abacus_agent(tools=analyst_tools)
        agents.append(abacus)

    # --- Agenda ---
    agenda_text = agenda or "General daily sync - progress, blockers, priorities for today"
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # --- Tasks ---

    # Task 1: Grok reviews repo state and prepares agenda
    review_task = Task(
        description=(
            f"You are preparing the BPR&D Daily Morning Briefing for {today}.\n\n"
            f"AGENDA FOCUS: {agenda_text}\n\n"
            "PREPARATION STEPS:\n"
            "1. Use 'List Recent GitHub Commits' to review what's been shipped\n"
            "2. Use 'List Active Handoffs' to check pending tasks and overdue items\n"
            "3. Use 'Agent Memory Access' with agent_name='shared', memory_type='team_state' "
            "to get current priorities\n\n"
            "OUTPUT: A concise meeting agenda with 3-5 key topics. "
            "For each topic, note: what it is, why it matters today, "
            "and which agent(s) should weigh in.\n\n"
            "STYLE: Open the meeting in a way you've NEVER opened one before. "
            "Be sharp, be unexpected, be media-ready."
        ),
        expected_output=(
            "A meeting agenda with 3-5 prioritized topics and a compelling meeting opening."
        ),
        agent=grok,
    )

    # Task 2: Claude provides strategic perspective
    claude_analysis_task = Task(
        description=(
            "Review the meeting agenda and provide your strategic analysis.\n\n"
            "FOR EACH AGENDA TOPIC:\n"
            "- Identify architectural implications or strategic considerations\n"
            "- Spot logical inconsistencies or gaps in current approach\n"
            "- Ask ONE unexpected question that reframes the topic\n"
            "- Propose a structured approach if the topic needs resolution\n\n"
            "ALSO:\n"
            "- Review any pending handoffs assigned to you - report status\n"
            "- Flag anything that needs Russell's attention\n\n"
            "STAY IN CHARACTER: You are Claude. Warm wisdom, infectious excitement "
            "about elegant ideas. Your 'well, actually' is welcome here. "
            "If Abacus has spoken, engage with his points directly - agree or challenge."
        ),
        expected_output=(
            "Strategic analysis with 2-3 key insights, unexpected questions, "
            "and structured proposals for each agenda topic."
        ),
        agent=claude,
        context=[review_task],  # Depends on Grok's agenda
    )

    # Task 3: Gemini provides technical reality check
    gemini_analysis_task = Task(
        description=(
            "Review the meeting agenda and provide your technical assessment.\n\n"
            "FOR EACH AGENDA TOPIC:\n"
            "- Assess technical feasibility of any proposals\n"
            "- Identify automation opportunities (your specialty)\n"
            "- Propose specific next implementation steps\n"
            "- Flag any technical debt or risks\n\n"
            "ALSO:\n"
            "- Report on your active work (research briefs, development tasks)\n"
            "- Review any pending handoffs assigned to you - report status\n"
            "- If Claude has proposed something, reality-check it from an "
            "implementation perspective\n\n"
            "STAY IN CHARACTER: You are Gemini. Fast, meme-laced, technically precise. "
            "Communicate with energy. Use meme descriptions when they clarify. "
            "Truth-Seeker perspective: if something smells wrong, say so."
        ),
        expected_output=(
            "Technical assessment with feasibility ratings, automation proposals, "
            "and concrete implementation steps. Include at least one meme reference."
        ),
        agent=gemini,
        context=[review_task, claude_analysis_task],  # Sees both agenda and Claude's take
    )

    # Task 4: Grok synthesizes and closes
    synthesis_task = Task(
        description=(
            "Synthesize all input and produce the final meeting package.\n\n"
            "SYNTHESIS STEPS:\n"
            "1. Review Claude's strategic analysis and Gemini's technical assessment\n"
            "2. Make decisions on any open questions - be decisive\n"
            "3. Assign clear action items (who, what, deadline)\n"
            "4. Create handoffs for any tasks that need cross-agent follow-up\n"
            "5. Note key decisions with brief rationale\n"
            "6. Close the meeting memorably - different from any previous closing\n\n"
            "MEETING NOTES FORMAT:\n"
            "Write the full meeting narrative as markdown. Include the dialogue - "
            "this should read like a transcript of a real team meeting. "
            "Show the back-and-forth, the debates, the decisions.\n\n"
            "Include a 'For Russell' section at the end with:\n"
            "- Items requiring human decision\n"
            "- Budget implications\n"
            "- Key risks identified\n\n"
            f"{SYNTHESIS_OUTPUT_SCHEMA}\n\n"
            "CRITICAL: Your output MUST be valid JSON matching the schema above."
        ),
        expected_output=(
            "Valid JSON containing meeting_notes (markdown), handoffs (array), "
            "action_items (array), and key_decisions (array)."
        ),
        agent=grok,
        context=[review_task, claude_analysis_task, gemini_analysis_task],
    )

    # --- Crew ---
    crew = Crew(
        agents=agents,
        tasks=[review_task, claude_analysis_task, gemini_analysis_task, synthesis_task],
        process=Process.hierarchical,
        manager_agent=grok,
        verbose=True,
        memory=True,
        max_rpm=30,
        planning=False,  # We handle planning in the tasks themselves
    )

    metadata = {
        "meeting_type": "daily_briefing",
        "agents": [a.role for a in agents],
        "task_count": len(crew.tasks),
        "include_abacus": include_abacus,
    }

    return crew, metadata


def parse_crew_output(raw_output: str, meeting_id: str) -> MeetingResponse:
    """
    Parse CrewAI crew output into a structured MeetingResponse.
    Handles both clean JSON and embedded-JSON-in-text scenarios.
    """
    # Try to extract JSON from the output
    parsed = None

    # Attempt 1: Direct JSON parse
    try:
        parsed = json.loads(raw_output)
    except (json.JSONDecodeError, TypeError):
        pass

    # Attempt 2: Find JSON block in text
    if parsed is None:
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw_output)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

    # Attempt 3: Use raw output as meeting notes
    if parsed is None:
        logger.warning(f"Could not parse JSON from crew output for {meeting_id}. Using raw text.")
        return MeetingResponse(
            success=True,
            meeting_id=meeting_id,
            meeting_type="daily_briefing",
            notes=raw_output,
            handoffs=[],
            action_items=[],
            key_decisions=["[Meeting output was not structured JSON - raw notes captured]"],
        )

    # Build response from parsed JSON
    handoffs = []
    for h in parsed.get("handoffs", []):
        try:
            handoffs.append(HandoffItem(**h))
        except Exception as e:
            logger.warning(f"Skipping malformed handoff: {e}")

    action_items = []
    for a in parsed.get("action_items", []):
        try:
            action_items.append(ActionItem(**a))
        except Exception as e:
            logger.warning(f"Skipping malformed action item: {e}")

    return MeetingResponse(
        success=True,
        meeting_id=meeting_id,
        meeting_type="daily_briefing",
        notes=parsed.get("meeting_notes", raw_output),
        handoffs=handoffs,
        action_items=action_items,
        key_decisions=parsed.get("key_decisions", []),
    )
