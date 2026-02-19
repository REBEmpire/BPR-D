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
from tools.github_tool import commit_file, read_file

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
    success = True

    # 1. Commit meeting notes
    now = datetime.utcnow()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")
    meeting_type = response.meeting_type.replace("_", "-")
    notes_path = f"_agents/_sessions/{date}-{meeting_type}-{time_str}.md"
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

    # 3. Commit agent instructions to each agent's handoff queue
    # Architecture note:
    #   _agents/{agent}/handoff.md     = Agent's current task queue (table view, shown on TEAM page)
    #   _agents/_handoffs/{id}.md      = Individual task tickets (detailed, for traceability)
    # These are complementary views, not duplicates. Daily Briefing populates handoff.md.
    # Work Sessions use the write_file tool directly — they do NOT write agent_instructions JSON.
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


async def generate_and_commit_context_update(
    agent_name: str,
    provider: "LLMProvider",
    meeting_summary: str,
    assigned_items: list[str],
    cost_tracker: "CostTracker",
) -> bool:
    """Generate and commit an updated context/active.md for an agent post-Daily Briefing.

    Makes a single constrained LLM call using the agent's own provider to produce
    updated active.md content based on what was discussed in the meeting.
    Returns True on success. Failure is logged but non-blocking.
    """
    date = datetime.utcnow().strftime("%Y-%m-%d")
    context_path = f"_agents/{agent_name}/context/active.md"

    # Read current active.md to use as a formatting template
    current = await read_file(context_path)
    if current.startswith("Error") or current.startswith("File '"):
        current = "No existing context file found. Use the standard active.md format."

    # Build items summary
    items_text = "\n".join(f"- {item}" for item in assigned_items[:10]) if assigned_items else "No items assigned."

    prompt = (
        f"The team just completed a Daily Briefing. Here is what was discussed and decided:\n\n"
        f"## Meeting Summary\n{meeting_summary[:2000]}\n\n"
        f"## Your Assigned Action Items\n{items_text}\n\n"
        f"## Your Previous Context File\n{current[:2000]}\n\n"
        f"Update your active.md context file to reflect the outcome of this meeting. "
        f"Keep it under 400 words. Follow the EXACT format of your previous context file. "
        f"Update all sections: Current Status, Feelings & Observations, Recent Wins, "
        f"Looking Forward To, Team Snapshot, Blockers. "
        f"Output ONLY the markdown content, starting with the YAML front-matter (---). "
        f"Use 'Generated by: {agent_name.title()} | Model: {provider.model}' "
        f"and 'Last Updated: {date}' in the front-matter."
    )

    system = (
        f"You are {agent_name.title()}, a member of the BPR&D AI team. "
        f"Update your personal active context file honestly and concisely based on the meeting that just happened."
    )

    try:
        response = await provider.chat(
            messages=[{"role": "user", "content": prompt}],
            system=system,
            temperature=0.4,
        )
        cost_tracker.record_usage(
            agent_name=agent_name,
            prompt_tokens=response.input_tokens,
            completion_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
        )

        result = await commit_file(
            path=context_path,
            content=response.content,
            message=f"Auto-update context: {agent_name} post-briefing {date}",
        )
        if result:
            logger.info(f"Updated context/active.md for {agent_name}")
        else:
            logger.error(f"Failed to commit context update for {agent_name}")
        return result

    except Exception as e:
        logger.error(f"Failed to generate context update for {agent_name}: {e}")
        return False
