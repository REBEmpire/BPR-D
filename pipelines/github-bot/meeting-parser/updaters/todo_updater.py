"""
Updates BPR&D_To_Do_List.md with action items from a processed meeting.

Rules:
- Small/quick action items → append rows to ## Active Items table
- Large items (handoffs with acceptance criteria) → reference row pointing to tasks/projects/
- Deduplication: skip if task text already present (case-insensitive substring match)
"""

import re
import logging
from datetime import date

logger = logging.getLogger(__name__)

TODO_PATH = "BPR&D_To_Do_List.md"
TABLE_HEADER = "| # | Task | Owner | Priority | Status | Added |"
TABLE_DIVIDER = "|---|------|-------|----------|--------|-------|"


def update_todo_list(meeting_data: dict) -> int:
    """Append new action items to the To-Do list. Returns count of items added."""
    try:
        with open(TODO_PATH, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"{TODO_PATH} not found")
        return 0

    existing_tasks = _extract_existing_tasks(content)
    today = date.today().isoformat()
    new_rows = []

    # Process quick action items
    for item in meeting_data.get("action_items", []):
        task = item.get("task", "").strip()
        if not task:
            continue
        if _is_duplicate(task, existing_tasks):
            logger.info(f"Skipping duplicate action item: {task[:60]}")
            continue
        owner = item.get("assigned_to", "Team").capitalize()
        priority = item.get("priority", "medium").upper()
        deadline = item.get("deadline") or today
        new_rows.append({
            "task": task,
            "owner": owner,
            "priority": priority,
            "added": deadline,
        })
        existing_tasks.append(task.lower())

    # Process large handoffs with acceptance criteria → reference row
    for h in meeting_data.get("handoffs", []):
        if not h.get("acceptance_criteria"):
            continue  # No acceptance criteria = not a project file
        task_id = h.get("task_id", "")
        title = h.get("title", "").strip()
        if not title:
            continue
        ref_task = f"{title} _(see tasks/projects/{task_id}.md)_"
        if _is_duplicate(title, existing_tasks):
            logger.info(f"Skipping duplicate handoff reference: {title[:60]}")
            continue
        owner = h.get("assigned_to", "Team").capitalize()
        priority = h.get("priority", "medium").upper()
        deadline = h.get("due_date") or today
        new_rows.append({
            "task": ref_task,
            "owner": owner,
            "priority": priority,
            "added": deadline,
        })
        existing_tasks.append(title.lower())

    if not new_rows:
        logger.info("No new items to add to To-Do list")
        return 0

    # Find the next # number
    next_num = _get_next_row_number(content)
    rows_text = ""
    for i, row in enumerate(new_rows):
        rows_text += f"| {next_num + i} | {row['task']} | {row['owner']} | {row['priority']} | Pending | {row['added']} |\n"

    # Insert rows before the --- separator after the Active Items table
    content = _insert_rows(content, rows_text)
    with open(TODO_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Added {len(new_rows)} items to {TODO_PATH}")
    return len(new_rows)


def _extract_existing_tasks(content: str) -> list[str]:
    """Extract lowercase task text from all table rows."""
    tasks = []
    in_table = False
    for line in content.splitlines():
        if TABLE_HEADER in line or TABLE_DIVIDER in line:
            in_table = True
            continue
        if in_table and line.startswith("|") and "|" in line[1:]:
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 2 and cols[1]:
                tasks.append(cols[1].lower())
        elif in_table and not line.startswith("|"):
            # End of table section
            in_table = False
    return tasks


def _is_duplicate(task: str, existing: list[str]) -> bool:
    task_lower = task.lower()
    # Check if any existing task contains key words from new task (>60% overlap)
    task_words = set(task_lower.split())
    for existing_task in existing:
        existing_words = set(existing_task.split())
        if not task_words or not existing_words:
            continue
        overlap = len(task_words & existing_words) / min(len(task_words), len(existing_words))
        if overlap > 0.6:
            return True
    return False


def _get_next_row_number(content: str) -> int:
    """Find the highest row number in the Active Items table and return next."""
    numbers = re.findall(r"^\|\s*(\d+)\s*\|", content, re.MULTILINE)
    if numbers:
        return max(int(n) for n in numbers) + 1
    return 1


def _insert_rows(content: str, rows_text: str) -> str:
    """Insert new rows into the Active Items table."""
    # Find position: after the table divider row in Active Items section
    active_section = content.find("## Active Items")
    if active_section == -1:
        # Append before Completed Items
        completed = content.find("## Completed Items")
        if completed == -1:
            return content + "\n" + rows_text
        return content[:completed] + rows_text + "\n" + content[completed:]

    # Find the divider row after TABLE_HEADER
    divider_pos = content.find(TABLE_DIVIDER, active_section)
    if divider_pos == -1:
        return content + "\n" + rows_text

    # Insert after divider row
    insert_pos = content.index("\n", divider_pos) + 1
    return content[:insert_pos] + rows_text + content[insert_pos:]
