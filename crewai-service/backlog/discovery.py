"""
Backlog discovery for BPR&D work sessions.
Scans GitHub repo for open/pending items across:
  - _shared/handoff-living-to-do-list.md
  - _agents/**/*.md and _shared/**/*.md with status: pending/open
  - _agents/_handoffs/*.md with Status: open
  - _agents/roadmap-2026.json milestones with status: pending
  - projects/ and research/ top-level items with status: active/pending
Extracts top 3-5 highest priority items for the work session agent.
"""

import json
import logging
import re
from dataclasses import dataclass, field

from tools.github_tool import read_file

logger = logging.getLogger(__name__)

PRIORITY_RANK = {
    "critical": 0,
    "urgent": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}


@dataclass
class BacklogItem:
    title: str
    source: str  # file path where this was found
    priority: str = "medium"
    status: str = "pending"
    assigned_to: str = ""
    due_date: str = ""
    context: str = ""

    @property
    def priority_rank(self) -> int:
        return PRIORITY_RANK.get(self.priority.lower(), 3)


@dataclass
class BacklogResult:
    items: list[BacklogItem] = field(default_factory=list)
    sources_scanned: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def top_items(self) -> list[BacklogItem]:
        """Return top 5 items sorted by priority."""
        sorted_items = sorted(self.items, key=lambda x: x.priority_rank)
        return sorted_items[:5]

    def to_context_string(self) -> str:
        """Format backlog items as context for the agent prompt."""
        top = self.top_items
        if not top:
            return "No open backlog items found across the repository."

        lines = [f"## Open Backlog Items ({len(self.items)} total, showing top {len(top)})\n"]
        for i, item in enumerate(top, 1):
            lines.append(f"### {i}. {item.title}")
            lines.append(f"- **Source**: `{item.source}`")
            lines.append(f"- **Priority**: {item.priority}")
            lines.append(f"- **Status**: {item.status}")
            if item.assigned_to:
                lines.append(f"- **Assigned to**: {item.assigned_to}")
            if item.due_date:
                lines.append(f"- **Due**: {item.due_date}")
            if item.context:
                lines.append(f"- **Context**: {item.context[:200]}")
            lines.append("")
        return "\n".join(lines)

    def stats_line(self, actions_completed: int = 0, next_queued: int = 0) -> str:
        """Generate the mandated stats line for reports."""
        return (
            f"Backlog items processed: {len(self.top_items)} | "
            f"Actions completed: {actions_completed} | "
            f"Next items queued: {max(0, len(self.items) - len(self.top_items))}"
        )


async def discover_backlog() -> BacklogResult:
    """Scan the repo for all open/pending backlog items."""
    result = BacklogResult()

    # Run all discovery sources concurrently-ish (sequential for simplicity, but fast)
    await _scan_living_todo(result)
    await _scan_handoffs(result)
    await _scan_agent_handoffs(result)
    await _scan_roadmap(result)
    await _scan_shared_md(result)

    logger.info(
        f"Backlog discovery complete: {len(result.items)} items from "
        f"{result.sources_scanned} sources ({len(result.errors)} errors)"
    )
    return result


async def _scan_living_todo(result: BacklogResult) -> None:
    """Scan _shared/handoff-living-to-do-list.md for open items."""
    result.sources_scanned += 1
    content = await read_file("_shared/handoff-living-to-do-list.md")
    if content.startswith("Error"):
        # File doesn't exist yet — not an error, just empty
        logger.info("No living to-do list found at _shared/handoff-living-to-do-list.md")
        return

    _extract_markdown_tasks(content, "_shared/handoff-living-to-do-list.md", result)


async def _scan_handoffs(result: BacklogResult) -> None:
    """Scan _agents/_handoffs/*.md for open/pending handoff tasks."""
    result.sources_scanned += 1
    listing = await read_file("_agents/_handoffs")
    if listing.startswith("Error"):
        result.errors.append(f"Could not list _agents/_handoffs: {listing[:100]}")
        return

    # Parse directory listing for .md files
    md_files = []
    for line in listing.splitlines():
        line = line.strip()
        if "[file]" in line:
            fname = line.split("]")[-1].strip()
            if fname.endswith(".md"):
                md_files.append(fname)

    for fname in md_files:
        result.sources_scanned += 1
        path = f"_agents/_handoffs/{fname}"
        content = await read_file(path)
        if content.startswith("Error"):
            result.errors.append(f"Could not read {path}")
            continue

        # Parse handoff format: **Status**: open/pending
        status_match = re.search(r"\*\*Status\*\*:\s*(\w+)", content)
        status = status_match.group(1).lower() if status_match else ""

        if status not in ("open", "pending"):
            continue

        # Extract fields
        title_match = re.match(r"^#\s+(.+)", content, re.MULTILINE)
        title = title_match.group(1) if title_match else fname

        priority_match = re.search(r"\*\*Priority\*\*:\s*(\w+)", content)
        priority = priority_match.group(1).lower() if priority_match else "medium"

        assigned_match = re.search(r"\*\*Assigned to\*\*:\s*(\w+)", content)
        assigned = assigned_match.group(1) if assigned_match else ""

        due_match = re.search(r"\*\*Due date\*\*:\s*(\S+)", content)
        due = due_match.group(1) if due_match else ""

        context_match = re.search(r"## Context\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
        context = context_match.group(1).strip() if context_match else ""

        result.items.append(BacklogItem(
            title=title,
            source=path,
            priority=priority,
            status=status,
            assigned_to=assigned,
            due_date=due,
            context=context,
        ))


async def _scan_agent_handoffs(result: BacklogResult) -> None:
    """Scan _agents/{agent}/handoff.md for pending action items in tables."""
    for agent in ("grok", "claude", "gemini", "abacus"):
        result.sources_scanned += 1
        path = f"_agents/{agent}/handoff.md"
        content = await read_file(path)
        if content.startswith("Error"):
            continue

        # Parse markdown tables for rows with "Pending" status
        _extract_table_tasks(content, path, result)


async def _scan_roadmap(result: BacklogResult) -> None:
    """Scan _agents/roadmap-2026.json for pending milestones."""
    result.sources_scanned += 1
    content = await read_file("_agents/roadmap-2026.json")
    if content.startswith("Error"):
        result.errors.append("Could not read roadmap-2026.json")
        return

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        result.errors.append("roadmap-2026.json is not valid JSON")
        return

    for milestone in data.get("milestones", []):
        if milestone.get("status") in ("pending", "active"):
            # Map category to priority
            cat = milestone.get("category", "")
            points = milestone.get("points", 0)
            if points >= 40:
                priority = "high"
            elif points >= 20:
                priority = "medium"
            else:
                priority = "low"

            result.items.append(BacklogItem(
                title=f"[Roadmap] {milestone.get('title', 'Unknown')}",
                source="_agents/roadmap-2026.json",
                priority=priority,
                status=milestone.get("status", "pending"),
                context=milestone.get("description", ""),
            ))


async def _scan_shared_md(result: BacklogResult) -> None:
    """Scan _agents/_shared/ and _agents/ top-level md files for status fields."""
    for path in ("_agents/team_state.md", "_agents/PRE-LAUNCH-CHECKLIST.md"):
        result.sources_scanned += 1
        content = await read_file(path)
        if content.startswith("Error"):
            continue
        _extract_markdown_tasks(content, path, result)


def _extract_table_tasks(content: str, source: str, result: BacklogResult) -> None:
    """Extract tasks from markdown tables that have Pending/In Progress status."""
    # Match table rows: | Task | Assigned To | Priority | Status | Due |
    table_row_re = re.compile(
        r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|"
    )
    for match in table_row_re.finditer(content):
        task, assigned, priority, status, due = (
            match.group(1).strip(),
            match.group(2).strip(),
            match.group(3).strip(),
            match.group(4).strip(),
            match.group(5).strip(),
        )
        # Skip header rows
        if task.startswith("---") or task.lower() == "task":
            continue

        status_lower = status.lower()
        if status_lower in ("pending", "in progress", "blocked"):
            result.items.append(BacklogItem(
                title=task,
                source=source,
                priority=priority.lower(),
                status=status_lower,
                assigned_to=assigned,
                due_date=due if due != "TBD" else "",
            ))


def _extract_markdown_tasks(content: str, source: str, result: BacklogResult) -> None:
    """Extract tasks from markdown checklists (- [ ] items)."""
    checkbox_re = re.compile(r"^[-*]\s+\[\s*\]\s+(.+)", re.MULTILINE)
    for match in checkbox_re.finditer(content):
        task_text = match.group(1).strip()
        result.items.append(BacklogItem(
            title=task_text,
            source=source,
            priority="medium",
            status="pending",
        ))
