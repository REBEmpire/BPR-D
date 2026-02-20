"""
Updates each agent's handoff.md with new task assignments from a meeting.

Per-agent files: _agents/{agent}/handoff.md
Appends to the Active Tasks table(s).
Deduplication: skip if task_id or task text already present.
"""

import os
import re
import logging
from datetime import date

logger = logging.getLogger(__name__)

AGENTS = ["grok", "claude", "gemini", "abacus", "russell"]
HANDOFF_TABLE_HEADER = "| Task | Priority | Status | Due | Notes |"
HANDOFF_TABLE_DIVIDER = "|------|----------|--------|-----|-------|"


def update_handoffs(meeting_data: dict) -> dict[str, int]:
    """Update all relevant agent handoff files. Returns {agent: count} added."""
    # Group items by agent
    agent_items: dict[str, list[dict]] = {a: [] for a in AGENTS}

    for item in meeting_data.get("action_items", []):
        agent = item.get("assigned_to", "").lower()
        if agent in agent_items:
            agent_items[agent].append({
                "task": item.get("task", ""),
                "priority": item.get("priority", "medium").upper(),
                "deadline": item.get("deadline") or "",
                "notes": f"From session: {_session_basename(meeting_data)}",
                "task_id": "",
            })

    # Handoffs with acceptance_criteria go to tasks/projects; still add task row to agent handoff
    for h in meeting_data.get("handoffs", []):
        agent = h.get("assigned_to", "").lower()
        if agent in agent_items:
            task_id = h.get("task_id", "")
            task_ref = h.get("title", "")
            if h.get("acceptance_criteria"):
                task_ref += f" _(project: tasks/projects/{task_id}.md)_"
            agent_items[agent].append({
                "task": task_ref,
                "priority": h.get("priority", "medium").upper(),
                "deadline": h.get("due_date") or "",
                "notes": f"ID: {task_id}" if task_id else "",
                "task_id": task_id,
            })

    counts = {}
    for agent, items in agent_items.items():
        if not items:
            continue
        added = _update_agent_handoff(agent, items, meeting_data)
        if added > 0:
            counts[agent] = added

    return counts


def _update_agent_handoff(agent: str, items: list[dict], meeting_data: dict) -> int:
    handoff_path = f"_agents/{agent}/handoff.md"
    if not os.path.exists(handoff_path):
        logger.warning(f"Handoff file not found: {handoff_path}")
        return 0

    with open(handoff_path, encoding="utf-8") as f:
        content = f.read()

    existing = _extract_existing_tasks(content)
    new_rows = ""
    added = 0

    for item in items:
        task = item["task"].strip()
        if not task:
            continue
        if _is_duplicate(task, item.get("task_id", ""), existing):
            logger.info(f"[{agent}] Skipping duplicate: {task[:60]}")
            continue
        deadline = item["deadline"] or date.today().isoformat()
        notes = item["notes"] or ""
        new_rows += f"| {task} | {item['priority']} | PENDING | {deadline} | {notes} |\n"
        existing.append(task.lower())
        if item.get("task_id"):
            existing.append(item["task_id"].lower())
        added += 1

    if not new_rows:
        return 0

    # Insert into the first task table found
    content = _insert_into_table(content, new_rows, meeting_data)
    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"[{agent}] Added {added} task(s) to handoff.md")
    return added


def _extract_existing_tasks(content: str) -> list[str]:
    tasks = []
    for line in content.splitlines():
        if line.startswith("|") and "|" in line[1:]:
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 1 and cols[0] and not cols[0].startswith("-"):
                tasks.append(cols[0].lower())
    return tasks


def _is_duplicate(task: str, task_id: str, existing: list[str]) -> bool:
    if task_id and task_id.lower() in existing:
        return True
    task_lower = task.lower()
    task_words = set(task_lower.split())
    for e in existing:
        e_words = set(e.split())
        if not task_words or not e_words:
            continue
        overlap = len(task_words & e_words) / min(len(task_words), len(e_words))
        if overlap > 0.65:
            return True
    return False


def _insert_into_table(content: str, new_rows: str, meeting_data: dict) -> str:
    """Insert rows after the first table divider row found."""
    divider_pos = content.find(HANDOFF_TABLE_DIVIDER)
    if divider_pos == -1:
        # No table found — append a new section before the last --- or at end
        session_name = _session_basename(meeting_data)
        new_section = f"\n### From Meeting: {session_name}\n\n{HANDOFF_TABLE_HEADER}\n{HANDOFF_TABLE_DIVIDER}\n{new_rows}"
        # Append before trailing --- or at end
        last_divider = content.rfind("\n---")
        if last_divider > 0:
            return content[:last_divider] + new_section + content[last_divider:]
        return content + new_section

    insert_pos = content.index("\n", divider_pos) + 1
    return content[:insert_pos] + new_rows + content[insert_pos:]


def _session_basename(meeting_data: dict) -> str:
    path = meeting_data.get("session_file", "")
    return path.replace("\\", "/").split("/")[-1].replace(".md", "")
