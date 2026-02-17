"""
Markdown renderer for BPR&D meeting notes.
Converts transcript + structured data into formatted meeting notes
for GitHub storage at _agents/_sessions/YYYY-MM-DD-meeting.md.
"""

from datetime import datetime

from models.meeting import MeetingResponse


def render_meeting_notes(response: MeetingResponse) -> str:
    """Render a MeetingResponse into a full markdown document for GitHub."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    time_str = datetime.utcnow().strftime("%H:%M UTC")

    lines = [
        f"# {response.meeting_type.replace('_', ' ').title()} — {date}",
        f"*Meeting ID: {response.meeting_id} | {time_str}*\n",
    ]

    # Summary (at top for quick access)
    if response.summary:
        lines.append("## Summary\n")
        lines.append(response.summary)
        lines.append("")

    # For Russell (right after summary)
    if response.for_russell:
        lines.append("## For Russell\n")
        lines.append(response.for_russell)
        lines.append("")

    # Key decisions (executive-level info grouped at top)
    if response.key_decisions:
        lines.append("## Key Decisions\n")
        for decision in response.key_decisions:
            lines.append(f"- {decision}")
        lines.append("")

    # Full transcript
    if response.notes:
        lines.append("---\n")
        lines.append("## Full Transcript\n")
        lines.append(response.notes)
        lines.append("")

    # Action items
    if response.action_items:
        lines.append("## Action Items\n")
        lines.append("| Task | Assigned To | Priority | Deadline |")
        lines.append("|------|-------------|----------|----------|")
        for item in response.action_items:
            lines.append(
                f"| {item.task} | {item.assigned_to} | {item.priority} | {item.deadline or 'TBD'} |"
            )
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

    # Cost summary
    cost = response.cost_estimate
    lines.append("## Meeting Metrics\n")
    lines.append(f"- **Total Cost**: ${cost.cost_usd:.4f}")
    lines.append(f"- **Tokens**: {cost.total_tokens} ({cost.prompt_tokens} in / {cost.completion_tokens} out)")
    lines.append(f"- **Duration**: {cost.execution_time_seconds:.0f}s")
    if cost.by_agent:
        lines.append("- **By Agent**:")
        for agent, agent_cost in cost.by_agent.items():
            lines.append(f"  - {agent}: ${agent_cost:.4f}")
    if cost.terminated_early:
        lines.append(f"- **Early Termination**: {cost.termination_reason}")
    lines.append("")

    return "\n".join(lines)
