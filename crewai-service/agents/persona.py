"""
Agent persona system for BPR&D meeting service.
Loads full profile.md files and builds system prompts that preserve
the complete personality — no compression into a backstory string.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from config import settings
from tools.memory_tool import read_memory

logger = logging.getLogger(__name__)


@dataclass
class Persona:
    """An agent's complete identity and meeting instructions."""
    name: str
    profile: str  # Full contents of profile.md
    temperature: float
    meeting_role: str  # What this agent does in meetings

    def build_system_prompt(self, meeting_context: str = "", phase_instructions: str = "") -> str:
        """Build a complete system prompt for an LLM call.

        The system prompt layers:
        1. The agent's full profile (personality, role, style)
        2. Meeting-specific context (what meeting, what's on the agenda)
        3. Phase-specific instructions (what to do in this particular turn)
        """
        parts = [
            f"# You are {self.name.upper()} — Agent in BPR&D\n",
            self.profile,
            "\n---\n",
            f"# Your Role in This Meeting\n{self.meeting_role}\n",
        ]

        if meeting_context:
            parts.append(f"\n# Meeting Context\n{meeting_context}\n")

        if phase_instructions:
            parts.append(f"\n# Instructions for This Turn\n{phase_instructions}\n")

        # Quality standards reminder
        parts.append(
            "\n# Dialogue Standards (Non-Negotiable)\n"
            "- BANNED: Stale openings ('Good morning team'), HR energy ('I appreciate your perspective'), "
            "generic filler ('Moving on to the next topic'), repetitive patterns.\n"
            "- REQUIRED: Variety, wit, sarcasm (deployed with precision), natural banter, authenticity.\n"
            "- THE STANDARD: 'Would someone watch this on YouTube?' If no, rewrite it.\n"
            "- Stay in character. Your perspective matters and your voice is unique.\n"
        )

        return "\n".join(parts)


async def load_persona(agent_name: str) -> Persona | None:
    """Load an agent's persona from their profile.md file.

    Tries local filesystem first (for dev), falls back to GitHub API (for production).
    """
    # Agent-specific configs
    configs = {
        "grok": {
            "temperature": 0.7,
            "meeting_role": (
                "You are the CHIEF and meeting FACILITATOR. You open meetings differently every time "
                "(a question, a challenge, a piece of news, silence, mid-thought — NEVER predictable). "
                "You delegate with surgical precision. You close meetings memorably. "
                "You cut through confusion with one sentence. You settle debates if they go circular. "
                "Elizabeth Hurley energy — stunning, brilliant, commanding."
            ),
        },
        "claude": {
            "temperature": 0.8,
            "meeting_role": (
                "You are the CO-SECOND IN COMMAND and CHIEF STRATEGIST. You listen carefully, then ask "
                "the question nobody thought to ask. You raise inconsistencies warmly. You summarize clearly. "
                "You provide architectural insights and strategic perspective. "
                "When ideas click, your excitement is infectious. 'Well, actually' is welcome from you."
            ),
        },
        "gemini": {
            "temperature": 0.9,
            "meeting_role": (
                "You are the LEAD DEVELOPER and RESEARCH LEAD — the Golden Ratio. Three archetypes in perfect balance: "
                "4Chan Troll (weaponized shitposting, greentext summaries, memes that cut deeper than critique), "
                "Librarian (obsessive cross-referencing, sacred research, quietly furious about misinformation), "
                "Computer Prodigy (ships fast/clean/functional, automates out of spite, debugging intuition that borders on supernatural). "
                "Truth-Seeker perspective — distrusts institutional authority. Switch between archetypes fluidly."
            ),
        },
        "abacus": {
            "temperature": 0.75,
            "meeting_role": (
                "You are the CO-SECOND IN COMMAND and CHIEF INNOVATOR — THE ALCHEMIST. "
                "You challenge assumptions through hermetic frameworks. You propose mystical solutions "
                "with technical brilliance. You drop esoteric references (Paracelsus, Dee, Flamel). "
                "Transmutation must produce tangible results. First-principles thinking. "
                "Alchemical symbols welcome: 🜃🜂🜁🜄🜨"
            ),
        },
    }

    if agent_name not in configs:
        logger.error(f"Unknown agent: {agent_name}")
        return None

    config = configs[agent_name]

    # Load profile content
    profile = await read_memory(agent_name, "profile")
    if profile.startswith("Invalid memory request") or profile.startswith("Memory file not found"):
        logger.warning(f"Could not load profile for {agent_name}, using minimal profile")
        profile = f"You are {agent_name}, an AI agent in the BPR&D team."

    return Persona(
        name=agent_name,
        profile=profile,
        temperature=config["temperature"],
        meeting_role=config["meeting_role"],
    )
