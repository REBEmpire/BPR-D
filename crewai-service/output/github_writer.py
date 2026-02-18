"""
GitHub writer for BPR&D meeting service.
Commits meeting notes and handoff files to the GitHub repository.
"""

import logging
from datetime import datetime
from difflib import SequenceMatcher

from models.meeting import MeetingResponse, HandoffItem
from output.renderer import render_meeting_notes
from tools.github_tool import commit_file

logger = logging.getLogger(__name__)


def _deduplicate_handoffs(handoffs: list[HandoffItem]) -> list[HandoffItem]:
    """Remove duplicate handoffs with the same assignee and overlapping content.

    Conservative: only merges when same assigned_to AND title similarity > 0.6
    AND context similarity > 0.5. Keeps the one with more acceptance criteria.
    """
    if len(handoffs) <= 1:
        return handoffs

    deduplicated = []
    skip_indices: set[int] = set()

    for i, h1 in enumerate(handoffs):
        if i in skip_indices:
            continue

        merged = h1
        for j in range(i + 1, len(handoffs)):
            if j in skip_indices:
                continue

            h2 = handoffs[j]
            if h1.assigned_to.lower() != h2.assigned_to.lower():
                continue

            title_sim = SequenceMatcher(
                None, h1.title.lower(), h2.title.lower()
            ).ratio()
            context_sim = SequenceMatcher(
                None, h1.context.lower(), h2.context.lower()
            ).ratio()

            if title_sim > 0.6 and context_sim > 0.5:
                logger.info(
                    f"Deduplicating handoffs: '{h1.title}' and '{h2.title}' "
                    f"(title_sim={title_sim:.2f}, context_sim={context_sim:.2f})"
                )
                if len(h2.acceptance_criteria) > len(merged.acceptance_criteria):
                    merged = h2
                skip_indices.add(j)

        deduplicated.append(merged)

    if len(deduplicated) < len(handoffs):
        logger.info(
            f"Deduplicated {len(handoffs)} handoffs down to {len(deduplicated)}"
        )

    return deduplicated


async def commit_meeting_results(response: MeetingResponse) -> bool:
    """Commit meeting notes and handoffs to GitHub. Returns True if all succeed."""
    success = True

    # 1. Commit meeting notes
    date = datetime.utcnow().strftime("%Y-%m-%d")
    meeting_type = response.meeting_type.replace("_", "-")
    notes_path = f"_agents/_sessions/{date}-{meeting_type}.md"
    notes_content = render_meeting_notes(response)

    # Work sessions use the mandated commit message format
    if response.meeting_type == "work_session":
        commit_msg = f"Auto Work Session {date} — processed backlog items"
    else:
        commit_msg = f"Meeting notes: {response.meeting_type.replace('_', ' ').title()} {date}"

    result = await commit_file(
        path=notes_path,
        content=notes_content,
        message=commit_msg,
    )
    if not result:
        logger.error(f"Failed to commit meeting notes to {notes_path}")
        success = False

    # 2. Commit handoff files (individual tasks, deduplicated)
    for handoff in _deduplicate_handoffs(response.handoffs):
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

    # 3. Commit agent instructions (Work Session updates)
    if response.agent_instructions:
        for agent_name, instruction_content in response.agent_instructions.items():
            agent_path = f"_agents/{agent_name.lower()}/handoff.md"

            result = await commit_file(
                path=agent_path,
                content=instruction_content,
                message=f"Update handoff instructions for {agent_name}",
            )
            if not result:
                logger.error(f"Failed to commit agent instructions to {agent_path}")
                success = False

    return success


def _render_handoff(handoff: HandoffItem) -> str:
    """Render a handoff item as markdown with front-matter and table format."""
    date = datetime.utcnow().strftime("%Y-%m-%d")

    lines = [
        "---",
        f"date: \"{date}\"",
        f"author: \"{handoff.created_by}\"",
        "model: \"grok-4\"",
        "version: \"v1.0\"",
        f"status: \"{handoff.status}\"",
        "---\n",
        f"# {handoff.title}\n",
        f"**ID**: {handoff.task_id}",
        f"**Assigned to**: {handoff.assigned_to}",
        f"**Priority**: {handoff.priority}",
        f"**Due date**: {handoff.due_date or 'TBD'}",
        f"**Created by**: {handoff.created_by}\n",
        f"## Context\n{handoff.context}\n",
    ]

    if handoff.acceptance_criteria:
        lines.append("## Acceptance Criteria\n")
        lines.append("| Criterion | Status |")
        lines.append("|-----------|--------|")
        for c in handoff.acceptance_criteria:
            lines.append(f"| {c} | Pending |")
        lines.append("")

    if handoff.dependencies:
        lines.append("## Dependencies\n")
        for d in handoff.dependencies:
            lines.append(f"- {d}")
        lines.append("")

    return "\n".join(lines)
