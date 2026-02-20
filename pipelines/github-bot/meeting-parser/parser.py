"""
Session file parser for the Meeting Secretary Bot.
Extracts structured data from _agents/_sessions/*.md files.

Parse priority:
  1. JSON code block in Full Transcript (Grok synthesis output)
  2. Direct JSON parse of entire file content
  3. Largest JSON object found anywhere in text
  4. Markdown table extraction from ## Action Items section
"""

import json
import re
import logging

logger = logging.getLogger(__name__)

KNOWN_AGENTS = {"grok", "claude", "gemini", "abacus", "russell"}


def parse_session_file(filepath: str) -> dict:
    """Parse a session .md file and return structured meeting data."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Try JSON strategies first (Grok synthesis output)
    data = _try_json_code_block(content)
    if not data:
        data = _try_direct_json(content)
    if not data:
        data = _try_find_largest_json(content)

    if data:
        return _normalize_json(data, content, filepath)

    # Fallback: extract from markdown structure
    logger.warning(f"No JSON synthesis found in {filepath}, falling back to markdown extraction")
    return _extract_from_markdown(content, filepath)


def _try_json_code_block(text: str) -> dict | None:
    """Extract JSON from ```json ... ``` code block."""
    pattern = r"```(?:json)?\s*\n?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, dict) and _looks_like_synthesis(data):
                return data
        except json.JSONDecodeError:
            continue
    return None


def _try_direct_json(text: str) -> dict | None:
    try:
        data = json.loads(text.strip())
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return None


def _try_find_largest_json(text: str) -> dict | None:
    depth = 0
    start = None
    candidates = []
    for i, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                candidates.append(text[start:i + 1])
                start = None
    candidates.sort(key=len, reverse=True)
    for candidate in candidates:
        try:
            data = json.loads(candidate)
            if isinstance(data, dict) and _looks_like_synthesis(data):
                return data
        except json.JSONDecodeError:
            continue
    return None


def _looks_like_synthesis(data: dict) -> bool:
    """Check if this JSON looks like a Grok synthesis output."""
    return any(k in data for k in ("action_items", "handoffs", "meeting_notes", "key_decisions"))


def _normalize_json(data: dict, raw_content: str, filepath: str) -> dict:
    """Normalize Grok JSON synthesis into the secretary's canonical format."""
    action_items = []
    for a in data.get("action_items", []):
        if not isinstance(a, dict):
            continue
        action_items.append({
            "task": a.get("task", ""),
            "assigned_to": _normalize_agent(a.get("assigned_to", "team")),
            "priority": a.get("priority", "medium"),
            "deadline": a.get("deadline") or a.get("due_date"),
        })

    handoffs = []
    for h in data.get("handoffs", []):
        if not isinstance(h, dict):
            continue
        handoffs.append({
            "task_id": h.get("task_id", ""),
            "title": h.get("title", ""),
            "assigned_to": _normalize_agent(h.get("assigned_to", "team")),
            "priority": h.get("priority", "medium"),
            "due_date": h.get("due_date") or h.get("deadline"),
            "context": h.get("context", ""),
            "acceptance_criteria": h.get("acceptance_criteria", []),
            "status": h.get("status", "open"),
            "created_by": h.get("created_by", "grok"),
        })

    return {
        "session_file": filepath,
        "meeting_notes": data.get("meeting_notes", ""),
        "hic_summary": _extract_hic_summary(raw_content),
        "for_russell": data.get("for_russell", ""),
        "key_decisions": data.get("key_decisions", []),
        "action_items": action_items,
        "handoffs": handoffs,
        "session_date": _extract_date(raw_content, filepath),
        "session_type": _extract_session_type(raw_content, filepath),
    }


def _extract_from_markdown(content: str, filepath: str) -> dict:
    """Fallback: extract action items from ## Action Items markdown table."""
    action_items = []

    # Find the Action Items table
    table_match = re.search(
        r"## Action Items\s*\n\s*\|.+?\|\s*\n\s*\|[-| ]+\|\s*\n((?:\|.+\|\s*\n)+)",
        content,
        re.IGNORECASE
    )
    if table_match:
        for row in table_match.group(1).strip().splitlines():
            cols = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cols) >= 2 and cols[0]:
                action_items.append({
                    "task": cols[0],
                    "assigned_to": _normalize_agent(cols[1]) if len(cols) > 1 else "team",
                    "priority": cols[2].lower() if len(cols) > 2 else "medium",
                    "deadline": cols[4] if len(cols) > 4 else None,
                })

    return {
        "session_file": filepath,
        "meeting_notes": "",
        "hic_summary": _extract_hic_summary(content),
        "for_russell": _extract_section(content, "For Russell"),
        "key_decisions": [],
        "action_items": action_items,
        "handoffs": [],
        "session_date": _extract_date(content, filepath),
        "session_type": _extract_session_type(content, filepath),
    }


def _extract_hic_summary(content: str) -> str:
    match = re.search(r"## HiC Summary.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def _extract_section(content: str, section_name: str) -> str:
    pattern = rf"## {re.escape(section_name)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def _extract_date(content: str, filepath: str) -> str:
    # Try YAML frontmatter
    match = re.search(r'^date:\s*["\']?(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
    if match:
        return match.group(1)
    # Try filename
    fname = filepath.replace("\\", "/").split("/")[-1]
    match = re.match(r"(\d{4}-\d{2}-\d{2})", fname)
    if match:
        return match.group(1)
    return ""


def _extract_session_type(content: str, filepath: str) -> str:
    # Try H1 heading
    match = re.search(r"^# (.+?) —", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Try filename
    fname = filepath.replace("\\", "/").split("/")[-1].replace(".md", "")
    parts = fname.split("-")
    # Skip date prefix (YYYY-MM-DD = 3 parts)
    if len(parts) > 3:
        return " ".join(parts[3:]).replace("-", " ").title()
    return "Meeting"


def _normalize_agent(name: str) -> str:
    """Normalize agent name to lowercase known agent or 'team'."""
    if not name:
        return "team"
    name = name.lower().strip()
    if name in KNOWN_AGENTS:
        return name
    return name  # Keep as-is (could be 'russell', a team name, etc.)
