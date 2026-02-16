"""
Output parser for BPR&D meeting service.
Extracts structured JSON from Grok's synthesis output.
Multi-strategy: direct JSON → regex extraction → fallback to raw text.
"""

import json
import logging
import re

from models.meeting import HandoffItem, ActionItem

logger = logging.getLogger(__name__)


def parse_synthesis(raw: str) -> dict:
    """Parse Grok's synthesis output into structured data.

    Returns a dict with keys:
        meeting_notes: str
        handoffs: list[HandoffItem]
        action_items: list[ActionItem]
        key_decisions: list[str]
        for_russell: str
    """
    if not raw:
        return _empty_result()

    # Strategy 1: Direct JSON parse
    data = _try_direct_json(raw)
    if data:
        return _normalize(data)

    # Strategy 2: Extract JSON block from markdown code fence
    data = _try_extract_json_block(raw)
    if data:
        return _normalize(data)

    # Strategy 3: Extract JSON from anywhere in the text
    data = _try_find_json(raw)
    if data:
        return _normalize(data)

    # Fallback: Use raw text as meeting notes
    logger.warning("Could not parse structured JSON from synthesis, using raw text")
    return {
        "meeting_notes": raw,
        "handoffs": [],
        "action_items": [],
        "key_decisions": [],
        "for_russell": "",
    }


def _try_direct_json(text: str) -> dict | None:
    """Try parsing the entire text as JSON."""
    try:
        data = json.loads(text.strip())
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return None


def _try_extract_json_block(text: str) -> dict | None:
    """Extract JSON from a markdown ```json ... ``` code block."""
    pattern = r"```(?:json)?\s*\n?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return None


def _try_find_json(text: str) -> dict | None:
    """Find the largest JSON object in the text."""
    # Find all { ... } blocks
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
                candidates.append(text[start : i + 1])
                start = None

    # Try largest first
    candidates.sort(key=len, reverse=True)
    for candidate in candidates:
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return None


def _normalize(data: dict) -> dict:
    """Normalize parsed JSON into the expected structure."""
    result = {
        "meeting_notes": data.get("meeting_notes", ""),
        "key_decisions": data.get("key_decisions", []),
        "for_russell": data.get("for_russell", ""),
    }

    # Parse handoffs
    handoffs = []
    for h in data.get("handoffs", []):
        try:
            handoffs.append(HandoffItem(**h))
        except Exception as e:
            logger.warning(f"Invalid handoff data: {e}")
    result["handoffs"] = handoffs

    # Parse action items
    action_items = []
    for a in data.get("action_items", []):
        try:
            action_items.append(ActionItem(**a))
        except Exception as e:
            logger.warning(f"Invalid action item data: {e}")
    result["action_items"] = action_items

    return result


def _empty_result() -> dict:
    return {
        "meeting_notes": "",
        "handoffs": [],
        "action_items": [],
        "key_decisions": [],
        "for_russell": "",
    }
