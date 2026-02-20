"""
Delta-updates each agent's active.md with wins/blockers/current status from a meeting.

Strategy:
- Archives the current active.md to context/archive/
- Rewrites only the operational sections (Recent Wins, Blockers, Current Status)
- Preserves personality sections (Feelings & Observations, Looking Forward To, Team Snapshot, etc.)

Only updates agents who have action items or handoffs assigned to them in the meeting.
"""

import os
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

AGENTS = ["grok", "claude", "gemini", "abacus"]

# Sections we will update (case-insensitive)
UPDATABLE_SECTIONS = [
    "current status",
    "recent wins",
    "blockers",
]

# Sections we always preserve as-is
PRESERVE_SECTIONS = [
    "feelings & observations",
    "looking forward to",
    "team snapshot",
    "faction",
    "api budget request",
]


def update_active_contexts(meeting_data: dict) -> dict[str, bool]:
    """Update active.md for agents that have items in this meeting. Returns {agent: updated}."""
    # Determine which agents are mentioned in this meeting
    mentioned = _agents_mentioned(meeting_data)
    results = {}

    for agent in AGENTS:
        if agent not in mentioned:
            continue
        updated = _update_agent_active(agent, meeting_data)
        results[agent] = updated

    return results


def _agents_mentioned(meeting_data: dict) -> set[str]:
    mentioned = set()
    for item in meeting_data.get("action_items", []):
        a = item.get("assigned_to", "").lower()
        if a in AGENTS:
            mentioned.add(a)
    for h in meeting_data.get("handoffs", []):
        a = h.get("assigned_to", "").lower()
        if a in AGENTS:
            mentioned.add(a)
    return mentioned


def _update_agent_active(agent: str, meeting_data: dict) -> bool:
    active_path = f"_agents/{agent}/context/active.md"
    archive_dir = f"_agents/{agent}/context/archive"

    if not os.path.exists(active_path):
        logger.warning(f"active.md not found for {agent}: {active_path}")
        return False

    with open(active_path, encoding="utf-8") as f:
        current_content = f.read()

    # Archive current version
    os.makedirs(archive_dir, exist_ok=True)
    now = datetime.now(timezone.utc)
    archive_name = now.strftime("%Y-%m-%d-%H%M") + "-active.md"
    archive_path = os.path.join(archive_dir, archive_name)
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(current_content)

    # Build delta content for this agent
    session_name = _session_basename(meeting_data)
    session_date = meeting_data.get("session_date", now.strftime("%Y-%m-%d"))
    session_type = meeting_data.get("session_type", "Meeting")

    new_wins = _build_wins(agent, meeting_data, session_name)
    new_blockers = _build_blockers(agent, meeting_data)
    new_status = _build_status(agent, meeting_data, session_type)

    # Apply delta updates to content
    updated = current_content
    if new_status:
        updated = _replace_section(updated, "Current Status", new_status)
    if new_wins:
        updated = _prepend_to_section(updated, "Recent Wins", new_wins)
    if new_blockers:
        updated = _replace_section(updated, "Blockers", new_blockers)

    # Update the frontmatter Last Updated line
    updated = _update_frontmatter(updated, session_name, session_date, now)

    with open(active_path, "w", encoding="utf-8") as f:
        f.write(updated)

    logger.info(f"[{agent}] Updated active.md (archived to {archive_path})")
    return True


def _build_wins(agent: str, meeting_data: dict, session_name: str) -> str:
    """Build Recent Wins bullet for tasks newly assigned (shows agent has work)."""
    assigned_tasks = []
    for item in meeting_data.get("action_items", []):
        if item.get("assigned_to", "").lower() == agent:
            assigned_tasks.append(item.get("task", ""))
    for h in meeting_data.get("handoffs", []):
        if h.get("assigned_to", "").lower() == agent:
            assigned_tasks.append(h.get("title", ""))

    if not assigned_tasks:
        return ""

    session_date = meeting_data.get("session_date", "")
    lines = [f"- [ ] _{session_name}_: {t}" for t in assigned_tasks[:5] if t]
    return "\n".join(lines)


def _build_blockers(agent: str, meeting_data: dict) -> str:
    """Extract blocker mentions from hic_summary or for_russell text (agent-specific)."""
    # Simple heuristic: if any handoffs assigned to this agent are critical/high, note them
    critical_items = []
    for h in meeting_data.get("handoffs", []):
        if h.get("assigned_to", "").lower() == agent and h.get("priority") in ("critical", "high"):
            due = h.get("due_date", "")
            critical_items.append(f"- **{h.get('priority', '').upper()}**: {h.get('title', '')} (due {due})" if due else f"- **{h.get('priority', '').upper()}**: {h.get('title', '')}")
    return "\n".join(critical_items) if critical_items else ""


def _build_status(agent: str, meeting_data: dict, session_type: str) -> str:
    session_date = meeting_data.get("session_date", "")
    count = sum(
        1 for i in list(meeting_data.get("action_items", [])) + list(meeting_data.get("handoffs", []))
        if i.get("assigned_to", "").lower() == agent
    )
    if count == 0:
        return ""
    return f"Active — {count} task(s) assigned from {session_type} ({session_date})"


def _replace_section(content: str, section_name: str, new_body: str) -> str:
    """Replace a section's body content."""
    pattern = rf"(## {re.escape(section_name)}\s*\n)(.*?)(?=\n## |\Z)"
    replacement = rf"\g<1>{new_body}\n"
    result = re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
    if result == content:
        # Section not found — append it before the final --- or at end
        append_block = f"\n## {section_name}\n\n{new_body}\n"
        last_div = content.rfind("\n---")
        if last_div > 0:
            return content[:last_div] + append_block + content[last_div:]
        return content + append_block
    return result


def _prepend_to_section(content: str, section_name: str, new_items: str) -> str:
    """Prepend new items to a section (preserves existing content)."""
    pattern = rf"(## {re.escape(section_name)}\s*\n)"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        insert_pos = match.end()
        return content[:insert_pos] + new_items + "\n" + content[insert_pos:]
    # Section not found — append
    append_block = f"\n## {section_name}\n\n{new_items}\n"
    last_div = content.rfind("\n---")
    if last_div > 0:
        return content[:last_div] + append_block + content[last_div:]
    return content + append_block


def _update_frontmatter(content: str, session_name: str, session_date: str, now: datetime) -> str:
    """Update the Generated by and Last Updated lines in frontmatter."""
    now_str = now.strftime("%Y-%m-%d %H:%M UTC")

    # Update 'updated:' or 'Last Updated:' in frontmatter
    updated_line = f'updated: "{now_str} (auto: {session_name})"'
    content = re.sub(r'^updated:.*$', updated_line, content, flags=re.MULTILINE)

    # Update Generated by line anywhere in file
    gen_line = f"*Generated by: Meeting Secretary Bot | Model: secretary-bot-v1*"
    last_gen = re.search(r'\*Generated by:.*\*', content)
    if last_gen:
        content = content[:last_gen.start()] + gen_line + content[last_gen.end():]
    else:
        content += f"\n{gen_line}\n"

    # Update Last Updated line
    last_updated_line = f"*Last Updated: {now_str} — auto-updated from {session_name}*"
    last_upd = re.search(r'\*Last Updated:.*\*', content)
    if last_upd:
        content = content[:last_upd.start()] + last_updated_line + content[last_upd.end():]

    return content


def _session_basename(meeting_data: dict) -> str:
    path = meeting_data.get("session_file", "")
    return path.replace("\\", "/").split("/")[-1].replace(".md", "")
