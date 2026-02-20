"""
GitHub writer for BPR&D meeting service.
Commits meeting notes and handoff files to the GitHub repository.
"""

import logging
from datetime import datetime
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from models.meeting import MeetingResponse, HandoffItem
from output.renderer import render_meeting_notes
from tools.github_tool import commit_file, read_file, commit_multiple_files

if TYPE_CHECKING:
    from llm.base import LLMProvider
    from utils.cost_tracker import CostTracker

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


async def commit_meeting_results(response: MeetingResponse) -> tuple[bool, str]:
    """Commit meeting notes and handoffs to GitHub. Returns (success, notes_path)."""
    # 1. Prepare meeting notes
    now = datetime.utcnow()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")
    meeting_type = response.meeting_type.replace("_", "-")
    notes_path = f"meetings/logs/{date}-{meeting_type}-{time_str}.md"
    notes_content = render_meeting_notes(response)

    # Work sessions use the mandated commit message format
    if response.meeting_type == "work_session":
        commit_msg = f"Auto Work Session {date} — processed backlog items"
    else:
        commit_msg = f"Meeting notes: {response.meeting_type.replace('_', ' ').title()} {date}"

    # Initialize staged changes dictionary for atomic commit
    staged_changes = {notes_path: notes_content}

    # 2. Prepare handoff files (individual tasks, deduplicated)
    for handoff in _deduplicate_handoffs(response.handoffs):
        handoff_content = _render_handoff(handoff)
        handoff_path = f"_agents/_handoffs/{handoff.task_id}.md"
        staged_changes[handoff_path] = handoff_content

    # 3. Prepare agent instructions to each agent's handoff queue
    if response.agent_instructions:
        for agent_name, instruction_content in response.agent_instructions.items():
            agent_path = f"_agents/{agent_name.lower()}/handoff.md"
            staged_changes[agent_path] = instruction_content

    # 4. Prepare context updates
    if response.context_updates:
        context_changes = await get_context_updates_changes(response.context_updates)
        staged_changes.update(context_changes)

    # Perform atomic commit
    logger.info(f"Committing {len(staged_changes)} files atomically for {response.meeting_type}")
    success = await commit_multiple_files(
        changes=staged_changes,
        message=commit_msg,
    )

    if not success:
        logger.error(f"Failed to commit meeting results to GitHub ({len(staged_changes)} files)")

    return success, notes_path


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



async def get_context_updates_changes(updates: dict[str, str]) -> dict[str, str]:
    """Calculate changes for context updates, including archiving the previous version."""
    changes = {}
    if not updates:
        return changes

    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")

    for agent_name, new_content in updates.items():
        # Clean the content (remove code blocks if present)
        cleaned_content = new_content.strip()
        if cleaned_content.startswith("```markdown"):
            cleaned_content = cleaned_content[11:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]

        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        cleaned_content = cleaned_content.strip()

        # Define paths
        # Ensure agent_name is lower case
        agent_key = agent_name.lower()
        active_path = f"_agents/{agent_key}/context/active.md"
        archive_path = f"_agents/{agent_key}/context/archive/{date_str}-{time_str}-active.md"

        # 1. Archive current active.md if it exists
        current_content = await read_file(active_path)
        if current_content and not current_content.startswith("Error") and not current_content.startswith("File '"):
            # It exists, so stage it for archiving
            changes[archive_path] = current_content
            logger.info(f"Staged context archive for {agent_name} to {archive_path}")
        else:
            logger.info(f"No existing context to archive for {agent_name}")

        # 2. Stage new active.md
        changes[active_path] = cleaned_content
        logger.info(f"Staged updated active.md for {agent_name}")

    return changes
