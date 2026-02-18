"""
BPR&D Central Nervous System Injector
======================================
Loads the bprd-core skill graph context and prepends it to every agent prompt
as the VERY FIRST step — before persona, before backlog, before anything else.

Usage:
    injector = NervousSystemInjector()
    await injector.load()
    prompt = injector.inject(agent_name="claude", session_type="work_session", base_prompt=prompt)

Design:
    - Reads agent-specific hook from _shared/skill-graphs/bprd-core/agent-hooks/
    - Reads shared preamble (always first)
    - Reads navigation entry point (skill-graphs/navigation.md)
    - Caches all reads for the lifetime of the session (no repeated GitHub API calls)
    - Gracefully degrades: if graph files are missing, logs warning and injects fallback

Architecture:
    See [[skill-graphs/navigation]] and [[hook-shared-preamble]] for design rationale.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from tools.github_tool import read_file

logger = logging.getLogger(__name__)

SKILL_GRAPH_BASE = "_shared/skill-graphs/bprd-core"
AGENT_HOOKS_BASE = f"{SKILL_GRAPH_BASE}/agent-hooks"

# Maps agent names to their hook files
AGENT_HOOK_MAP: dict[str, str] = {
    "grok": f"{AGENT_HOOKS_BASE}/hook-grok.md",
    "claude": f"{AGENT_HOOKS_BASE}/hook-claude.md",
    "gemini": f"{AGENT_HOOKS_BASE}/hook-gemini.md",
    "abacus": f"{AGENT_HOOKS_BASE}/hook-abacus.md",
}

SHARED_PREAMBLE_PATH = f"{AGENT_HOOKS_BASE}/hook-shared-preamble.md"
NAVIGATION_PATH = f"{SKILL_GRAPH_BASE}/skill-graphs/navigation.md"
MOC_CORE_PATH = f"{SKILL_GRAPH_BASE}/MOC-Core.md"

# Fallback preamble if graph files are unreachable
FALLBACK_PREAMBLE = """
╔══════════════════════════════════════════════════════════════════╗
║  BPR&D CENTRAL NERVOUS SYSTEM — ACTIVE (fallback mode)         ║
╚══════════════════════════════════════════════════════════════════╝

You are operating inside BPR&D's central nervous system.
Skill graph at: _shared/skill-graphs/bprd-core/
Key skills: [[skill-handoff-protocols]] | [[skill-session-output-format]] | [[skill-cost-governance]]

ZERO SPOOFING. REAL DELIVERABLES ONLY. GitHub-first.
"""


@dataclass
class NervousSystemContext:
    """Loaded and cached skill graph context for one session."""

    shared_preamble: str = ""
    navigation: str = ""
    agent_hook: str = ""
    moc_core_summary: str = ""
    load_errors: list[str] = field(default_factory=list)
    loaded: bool = False


class NervousSystemInjector:
    """
    Prepends BPR&D's central nervous system context to every agent prompt.

    Call `await injector.load()` once per session, then `injector.inject()`
    for each agent call within that session.
    """

    def __init__(self) -> None:
        self._context = NervousSystemContext()

    async def load(self) -> None:
        """
        Load all skill graph context from GitHub. Caches results for this session.
        Called ONCE at the start of each meeting/work session.
        """
        logger.info("Loading BPR&D central nervous system context...")

        # Load all files in parallel-ish (sequential to respect GitHub rate limits)
        self._context.shared_preamble = await self._safe_read(SHARED_PREAMBLE_PATH)
        self._context.navigation = await self._safe_read(NAVIGATION_PATH)
        self._context.moc_core_summary = await self._load_moc_summary()
        self._context.loaded = True

        if self._context.load_errors:
            logger.warning(
                "Nervous system loaded with %d missing files: %s",
                len(self._context.load_errors),
                self._context.load_errors,
            )
        else:
            logger.info("Nervous system fully loaded — all skill graph files available.")

    async def load_agent_hook(self, agent_name: str) -> str:
        """Load the agent-specific hook. Called when building each agent's prompt."""
        hook_path = AGENT_HOOK_MAP.get(agent_name.lower())
        if not hook_path:
            logger.warning("No hook file for agent '%s' — using shared preamble only.", agent_name)
            return ""
        return await self._safe_read(hook_path)

    def inject(
        self,
        agent_name: str,
        session_type: str,
        base_prompt: str,
        model_id: str = "",
        agent_hook: str = "",
    ) -> str:
        """
        Prepend the nervous system context to an agent prompt.

        Args:
            agent_name: "grok", "claude", "gemini", or "abacus"
            session_type: "daily_briefing", "work_session", etc.
            base_prompt: The prompt that would have been sent without the injector
            model_id: LLM model identifier string
            agent_hook: Pre-loaded agent hook content (from load_agent_hook())

        Returns:
            Full prompt with nervous system context prepended
        """
        if not self._context.loaded:
            logger.error("inject() called before load() — using fallback preamble")
            return self._build_fallback(agent_name, session_type, base_prompt)

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Build the nervous system header
        ns_header = self._render_preamble(
            agent_name=agent_name,
            session_type=session_type,
            model_id=model_id,
            timestamp=now,
        )

        # Quick ref card from navigation skill
        nav_summary = self._extract_quick_ref(self._context.navigation)

        # Agent-specific hook (persona + domain entry points)
        hook_block = self._extract_hook_block(agent_hook)

        # Assemble in strict order (from hook-shared-preamble.md spec)
        sections = [
            ns_header,
        ]

        if nav_summary:
            sections.append(f"## Skill Graph Quick Reference\n{nav_summary}")

        if hook_block:
            sections.append(f"## Your Role & Protocol\n{hook_block}")

        sections.append("---\n")
        sections.append(base_prompt)

        return "\n\n".join(sections)

    def inject_sync(
        self,
        agent_name: str,
        session_type: str,
        base_prompt: str,
        model_id: str = "",
    ) -> str:
        """
        Synchronous inject using only the cached context (no additional reads).
        Use when you cannot await — the full async inject() is preferred.
        """
        return self.inject(
            agent_name=agent_name,
            session_type=session_type,
            base_prompt=base_prompt,
            model_id=model_id,
            agent_hook="",  # No agent hook in sync mode
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _safe_read(self, path: str) -> str:
        """Read a file from GitHub; return empty string on any error."""
        content = await read_file(path)
        if content.startswith("Error") or not content.strip():
            self._context.load_errors.append(path)
            return ""
        return content

    async def _load_moc_summary(self) -> str:
        """Load just the first section of MOC-Core for quick orientation."""
        content = await self._safe_read(MOC_CORE_PATH)
        if not content:
            return ""
        # Return first 800 chars — enough to orient without blowing context budget
        return content[:800]

    def _render_preamble(
        self,
        agent_name: str,
        session_type: str,
        model_id: str,
        timestamp: str,
    ) -> str:
        """Render the mandatory first block — always verbatim, always first."""
        return f"""╔══════════════════════════════════════════════════════════════════╗
║  BPR&D CENTRAL NERVOUS SYSTEM — ACTIVE                         ║
╚══════════════════════════════════════════════════════════════════╝

You are operating inside BPR&D's central nervous system.
Begin by reading [[skill-graphs/navigation]] before taking any action.

AGENT: {agent_name.title()} | SESSION: {session_type} | TIME: {timestamp}
MODEL: {model_id or "unknown"}
GRAPH: _shared/skill-graphs/bprd-core/ (30+ nodes, 4 MOCs)

CORE SKILLS TO KNOW:
  [[skill-handoff-protocols]]     — task creation and tracking
  [[skill-session-output-format]] — your required output structure
  [[skill-cost-governance]]       — budget you operate under ($20/month team)
  [[skill-initiative-rule]]       — if backlog is empty, do NOT idle
  [[skill-agent-self-evolution]]  — grow the graph via /reflect

ZERO SPOOFING. REAL DELIVERABLES ONLY. GITHUB-FIRST."""

    def _extract_quick_ref(self, navigation_content: str) -> str:
        """Pull the Quick Reference Card section from navigation.md."""
        if not navigation_content:
            return ""
        marker = "## Quick Reference Card"
        idx = navigation_content.find(marker)
        if idx == -1:
            return ""
        # Extract from marker to next ## or end, cap at 600 chars
        section = navigation_content[idx + len(marker) :].strip()
        next_section = section.find("\n##")
        if next_section > 0:
            section = section[:next_section]
        return section[:600].strip()

    def _extract_hook_block(self, hook_content: str) -> str:
        """Pull the Hook Block section (the verbatim prompt text) from a hook file."""
        if not hook_content:
            return ""
        # Look for the fenced code block that contains the prompt
        start = hook_content.find("```\n")
        if start == -1:
            return ""
        end = hook_content.find("\n```", start + 4)
        if end == -1:
            return hook_content[start + 4 :][:1200]
        return hook_content[start + 4 : end][:1200]

    def _build_fallback(self, agent_name: str, session_type: str, base_prompt: str) -> str:
        """Emergency fallback when load() was not called."""
        return f"{FALLBACK_PREAMBLE}\n\nAGENT: {agent_name} | SESSION: {session_type}\n\n---\n\n{base_prompt}"
