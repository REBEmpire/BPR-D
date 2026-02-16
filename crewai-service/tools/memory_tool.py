"""
Agent memory tool for BPR&D meeting service.
Provides access to the _agents/ memory system during meetings.
Tries filesystem first (local dev), falls back to GitHub API (production).
"""

import base64
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
REPO = settings.GITHUB_REPO


def _headers() -> dict:
    return {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def _resolve_path(agent_name: str, memory_type: str) -> str | None:
    """Map agent + type to a relative path under _agents/."""
    if agent_name == "shared":
        paths = {
            "team_state": "team_state.md",
            "user_context": "_shared/user_context.md",
            "protocols": "_protocols.md",
        }
        return paths.get(memory_type)

    if agent_name not in ("grok", "claude", "gemini", "abacus"):
        return None

    paths = {
        "profile": f"{agent_name}/profile.md",
        "context": f"{agent_name}/context/active.md",
        "learnings": f"{agent_name}/learnings/latest.md",
    }
    return paths.get(memory_type)


async def read_memory(agent_name: str, memory_type: str) -> str:
    """Read from the agent memory system."""
    path = _resolve_path(agent_name.lower(), memory_type.lower())
    if path is None:
        return (
            f"Invalid memory request: agent='{agent_name}', type='{memory_type}'. "
            f"Valid agents: grok, claude, gemini, abacus, shared. "
            f"Valid types: profile, context, learnings, team_state, user_context, protocols."
        )

    # Try filesystem first (local dev)
    local_path = settings.AGENTS_DIR / path
    if local_path.exists():
        try:
            content = local_path.read_text(encoding="utf-8")
            if len(content) > 6000:
                content = content[:6000] + "\n\n... [truncated]"
            return content
        except Exception as e:
            logger.warning(f"Error reading local file {local_path}: {e}")

    # Fall back to GitHub API (production)
    github_path = f"_agents/{path}"
    url = f"{GITHUB_API}/repos/{REPO}/contents/{github_path}"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            if len(content) > 6000:
                content = content[:6000] + "\n\n... [truncated]"
            return content
        except httpx.HTTPError as e:
            return f"Memory file not found: {github_path} ({e})"
