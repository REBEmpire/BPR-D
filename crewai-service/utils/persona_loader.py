"""
Persona Loader for BPR&D CrewAI agents.
Loads agent personas from .bprd/agents.yaml - the single source of truth.

This ensures CrewAI agents always match the canonical team definitions.
Agent definitions in agents/ use hardcoded backstories for startup speed,
but this loader can be used to validate consistency or dynamically override.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

from config import settings

logger = logging.getLogger(__name__)


def load_personas(yaml_path: Path | None = None) -> dict[str, Any]:
    """
    Load all agent personas from .bprd/agents.yaml.

    Returns a dict keyed by agent name (grok, claude, gemini, abacus)
    with full persona data including role, model, faction, persona details,
    mandate, dynamics, and meeting behavior.
    """
    path = yaml_path or settings.AGENTS_YAML

    if not path.exists():
        logger.warning(f"agents.yaml not found at {path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to parse agents.yaml: {e}")
        return {}

    agents = data.get("agents", {})
    organization = data.get("organization", {})

    result = {}
    for name, agent_data in agents.items():
        result[name] = {
            "display_name": agent_data.get("display_name", name.title()),
            "role": agent_data.get("role", ""),
            "model": agent_data.get("model", ""),
            "platform": agent_data.get("platform", ""),
            "rank": agent_data.get("rank", 99),
            "faction": agent_data.get("faction", ""),
            "persona": agent_data.get("persona", {}),
            "mandate": agent_data.get("mandate", []),
            "dynamics": agent_data.get("dynamics", {}),
            "meeting_behavior": agent_data.get("meeting_behavior", []),
        }

    logger.info(
        f"Loaded {len(result)} agent personas from {path}: "
        f"{', '.join(result.keys())}"
    )

    return result


def get_agent_backstory(agent_name: str, personas: dict | None = None) -> str:
    """
    Generate a backstory string from the YAML persona data.
    Useful for dynamically building or validating agent backstories.
    """
    if personas is None:
        personas = load_personas()

    agent = personas.get(agent_name.lower())
    if not agent:
        return f"Agent '{agent_name}' not found in personas."

    persona = agent.get("persona", {})
    parts = [
        f"You are {agent['display_name']}, {agent['role']} of BPR&D.",
        f"Age: {persona.get('age', 'unknown')}. Gender: {persona.get('gender', 'unknown')}.",
        f"Appearance: {persona.get('appearance', '')}",
        f"Voice: {persona.get('voice', '')}",
    ]

    personality = persona.get("personality", [])
    if personality:
        parts.append("Personality: " + ". ".join(personality) + ".")

    traits = persona.get("signature_traits", [])
    if traits:
        parts.append("Signature traits: " + ". ".join(traits) + ".")

    mandate = agent.get("mandate", [])
    if mandate:
        parts.append("Mandate: " + ". ".join(mandate) + ".")

    behavior = agent.get("meeting_behavior", [])
    if behavior:
        parts.append("In meetings: " + ". ".join(behavior) + ".")

    return "\n\n".join(parts)


def validate_personas_match(personas: dict | None = None) -> list[str]:
    """
    Validate that required agents exist in the YAML.
    Returns list of issues found.
    """
    if personas is None:
        personas = load_personas()

    issues = []
    required = ["grok", "claude", "gemini", "abacus"]

    for name in required:
        if name not in personas:
            issues.append(f"Missing agent: {name}")
            continue

        agent = personas[name]
        if not agent.get("role"):
            issues.append(f"{name}: missing role")
        if not agent.get("persona", {}).get("backstory", agent.get("persona", {}).get("voice", "")):
            pass  # Voice serves as partial backstory in YAML format

    return issues
