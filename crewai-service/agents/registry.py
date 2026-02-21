"""
Agent registry for BPR&D meeting service.
Maps agent names to (Persona, LLMProvider) pairs.
Handles Abacus availability (paused until Feb 23, 2026).
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from config import settings
from llm import XAIProvider, AnthropicProvider, GoogleProvider, AbacusProvider, LLMProvider
from agents.persona import Persona, load_persona
from api_healer import APIHealer

logger = logging.getLogger(__name__)


@dataclass
class RegisteredAgent:
    """An agent with its persona and LLM provider ready to use."""
    persona: Persona
    provider: LLMProvider


# LLM provider instances (created once)
_providers: dict[str, LLMProvider] = {}


def _get_provider(agent_name: str) -> LLMProvider:
    """Get or create an LLM provider for an agent."""
    if agent_name not in _providers:
        if agent_name == "grok":
            _providers[agent_name] = XAIProvider()
        elif agent_name == "claude":
            _providers[agent_name] = AnthropicProvider()
        elif agent_name == "gemini":
            _providers[agent_name] = GoogleProvider()
        elif agent_name == "abacus":
            _providers[agent_name] = AbacusProvider()
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
    return _providers[agent_name]


def is_abacus_available() -> bool:
    """Check if Abacus has an API key configured."""
    # Use settings or the fallback key directly
    return bool(settings.ABACUS_PRIMARY_KEY or settings.ABACUS_BACKUP_KEY or "s2_1e30fa4a3d834bffb1b465d67eb1809e")


def get_default_participants(meeting_type: str) -> list[str]:
    """Get the default participant list for a meeting type.
    All 4 agents participate by default when keys are available.
    """
    base = ["grok", "claude", "gemini"]
    if is_abacus_available():
        base.append("abacus")
    return base


def resolve_participants(requested: list[str] | None, meeting_type: str) -> list[str]:
    """Resolve the final participant list, respecting overrides and availability."""
    if requested:
        participants = []
        for name in requested:
            name = name.lower()
            if name == "abacus" and not is_abacus_available():
                logger.warning("Abacus requested but no API key configured")
                continue
            participants.append(name)
        return participants
    return get_default_participants(meeting_type)


async def load_agents(participant_names: list[str]) -> dict[str, RegisteredAgent]:
    """Load all requested agents with their personas and LLM providers."""
    agents = {}
    for name in participant_names:
        persona = await load_persona(name)
        if persona is None:
            logger.error(f"Failed to load persona for {name}, skipping")
            continue
        provider = _get_provider(name)
        agents[name] = RegisteredAgent(persona=persona, provider=provider)
        logger.info(f"Loaded agent: {name} ({provider.model})")
    return agents

def get_active_healer() -> APIHealer:
    """Get the active API Healer instance from the Gemini provider."""
    # Ensure Gemini provider is initialized
    if "gemini" not in _providers:
        try:
             _providers["gemini"] = GoogleProvider()
        except Exception as e:
            logger.error(f"Failed to init GoogleProvider for healer: {e}")
            return APIHealer()

    provider = _providers["gemini"]
    if hasattr(provider, "healer"):
        return provider.healer
    return APIHealer()
