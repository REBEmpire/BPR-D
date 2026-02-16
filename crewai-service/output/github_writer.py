"""
GitHub writer for BPR&D meeting service.
Commits meeting notes and handoff files to the GitHub repository.
"""

import logging
from datetime import datetime

from models.meeting import MeetingResponse, HandoffItem
from output.renderer import render_meeting_notes
from tools.github_tool import commit_file

logger = logging.getLogger(__name__)


async def commit_meeting_results(response: MeetingResponse) -> bool:
    """Commit meeting notes and handoffs to GitHub. Returns True if all succeed."""
    success = True

    # 1. Commit meeting notes
    date = datetime.utcnow().strftime("%Y-%m-%d")
    meeting_type = response.meeting_type.replace("_", "-")
    notes_path = f"_agents/_sessions/{date}-{meeting_type}.md"
    notes_content = render_meeting_notes(response)

    result = await commit_file(
        path=notes_path,
        content=notes_content,
        message=f"Meeting notes: {response.meeting_type.replace('_', ' ').title()} {date}",
    )
    if not result:
        logger.error(f"Failed to commit meeting notes to {notes_path}")
        success = False

    # 2. Commit handoff files
    for handoff in response.handoffs:
        handoff_content = _render_handoff(handoff)
        handoff_path = f"_agents/_handoffs/{handoff.task_id}.md"

        result = await commit_file(
            path=handoff_path,
            content=handoff_content,
            message=f"Handoff: {handoff.title}",
        )
        if not result:
            logger.error(f"Failed to commit handoff {handoff.task_id}")
            success = False

    return success


def _render_handoff(handoff: HandoffItem) -> str:
    """Render a handoff item as markdown."""
    lines = [
        f"# {handoff.title}\n",
        f"**ID**: {handoff.task_id}",
        f"**Assigned to**: {handoff.assigned_to}",
        f"**Priority**: {handoff.priority}",
        f"**Due date**: {handoff.due_date or 'TBD'}",
        f"**Status**: {handoff.status}",
        f"**Created by**: {handoff.created_by}\n",
        f"## Context\n{handoff.context}\n",
    ]

    if handoff.acceptance_criteria:
        lines.append("## Acceptance Criteria\n")
        for c in handoff.acceptance_criteria:
            lines.append(f"- [ ] {c}")
        lines.append("")

    if handoff.dependencies:
        lines.append("## Dependencies\n")
        for d in handoff.dependencies:
            lines.append(f"- {d}")
        lines.append("")

    return "\n".join(lines)
