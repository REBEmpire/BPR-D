"""
Markdown renderer for BPR&D meeting notes.
Converts transcript + structured data into formatted meeting notes
for GitHub storage at _agents/_sessions/YYYY-MM-DD-meeting.md.

v1.1: Boss Girl's 5 Mandates — front-matter, HiC Summary, table Action Items,
      standardized Session Cost block with monthly running total.
"""

from datetime import datetime

from models.meeting import MeetingResponse
from utils.cost_tracker import load_monthly_spend


def render_meeting_notes(response: MeetingResponse) -> str:
    """Render a MeetingResponse into a full markdown document for GitHub."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    time_str = datetime.utcnow().strftime("%H:%M UTC")
    meeting_title = response.meeting_type.replace("_", " ").title()

    lines = []

    # Front-matter block (Mandate 1)
    lines.append("---")
    lines.append(f"Date: {date}")
    lines.append("Author: Meeting Engine (Grok synthesis) | Model: grok-4")
    lines.append("Version: v1.0")
    lines.append("Status: Active")
    lines.append("---\n")

    lines.append(f"# {meeting_title} — {date}")
    lines.append(f"*Meeting ID: {response.meeting_id} | {time_str}*\n")

    # HiC Summary (Mandate 4 — mandatory, <5 min read)
    lines.append("## HiC Summary (5-Minute Read)\n")
    if response.summary:
        lines.append(response.summary)
    else:
        lines.append("No summary generated this session.")
    lines.append("")

    # For Russell (mandatory — even if empty)
    lines.append("## For Russell\n")
    if response.for_russell:
        lines.append(response.for_russell)
    else:
        lines.append("None required this session.")
    lines.append("")

    # Key decisions (mandatory — even if empty)
    lines.append("## Key Decisions\n")
    if response.key_decisions:
        for decision in response.key_decisions:
            lines.append(f"- {decision}")
    else:
        lines.append("None this session.")
    lines.append("")

    # Action items (Mandate 2 — table format, mandatory)
    lines.append("## Action Items\n")
    lines.append("| Task | Assigned To | Priority | Status | Due |")
    lines.append("|------|-------------|----------|--------|-----|")
    if response.action_items:
        for item in response.action_items:
            lines.append(
                f"| {item.task} | {item.assigned_to} | {item.priority} "
                f"| Pending | {item.deadline or 'TBD'} |"
            )
    lines.append("")

    # Separator before transcript
    lines.append("---\n")

    # Full transcript
    lines.append("## Full Transcript\n")
    if response.notes:
        lines.append(response.notes)
    else:
        lines.append("No transcript recorded.")
    lines.append("")

    # Handoffs
    if response.handoffs:
        lines.append("## Handoffs Created\n")
        for h in response.handoffs:
            lines.append(f"### {h.title}")
            lines.append(f"- **ID**: {h.task_id}")
            lines.append(f"- **Assigned to**: {h.assigned_to}")
            lines.append(f"- **Priority**: {h.priority}")
            lines.append(f"- **Due**: {h.due_date or 'TBD'}")
            lines.append(f"- **Context**: {h.context}")
            if h.acceptance_criteria:
                lines.append("- **Acceptance Criteria**:")
                for c in h.acceptance_criteria:
                    lines.append(f"  - {c}")
            lines.append("")

    # Separator before cost
    lines.append("---\n")

    # Session Cost (Mandate 3 — standardized two-table format)
    cost = response.cost_estimate
    lines.append("## Session Cost\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Cost | ${cost.cost_usd:.4f} |")
    lines.append(
        f"| Total Tokens | {cost.total_tokens} "
        f"({cost.prompt_tokens} in / {cost.completion_tokens} out) |"
    )
    lines.append(f"| Duration | {cost.execution_time_seconds:.0f}s |")
    lines.append(f"| Session Type | {meeting_title} |")
    lines.append(f"| Meeting ID | {response.meeting_id} |")
    lines.append("")

    if cost.by_agent:
        lines.append("**By Agent:**\n")
        lines.append("| Agent | Cost | Tokens In | Tokens Out |")
        lines.append("|-------|------|-----------|------------|")
        for agent, agent_cost in cost.by_agent.items():
            lines.append(f"| {agent} | ${agent_cost:.4f} | — | — |")
        lines.append("")

    if cost.terminated_early:
        lines.append(f"**Early Termination**: {cost.termination_reason}\n")

    # Monthly running total
    monthly_total = load_monthly_spend() + cost.cost_usd
    lines.append(f"**Monthly Running Total:** ${monthly_total:.2f} of $20.00 budget used")
    lines.append("")

    return "\n".join(lines)
