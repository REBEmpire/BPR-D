"""
Agent Memory Tool for BPR&D CrewAI agents.
Provides access to the _agents/ memory system during meetings.

Priority: Phase 1 tool (second priority after GitHub per Grok's directive).

In production on Render, this uses the GitHub API to read memory files.
In local development, it reads directly from the filesystem.
"""

import base64
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config import settings


GITHUB_API = "https://api.github.com"
REPO = settings.GITHUB_REPO


def _headers() -> dict:
    return {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


class MemoryInput(BaseModel):
    agent_name: str = Field(
        description=(
            "Agent whose memory to access: 'grok', 'claude', 'gemini', or 'abacus'. "
            "Use 'shared' for team-wide resources."
        ),
    )
    memory_type: str = Field(
        description=(
            "Type of memory to retrieve: "
            "'profile' (agent persona and role), "
            "'context' (current work state and priorities), "
            "'learnings' (accumulated experience), "
            "'team_state' (overall team priorities - use with agent_name='shared'), "
            "'user_context' (Russell's preferences - use with agent_name='shared'), "
            "'protocols' (collaboration rules - use with agent_name='shared')."
        ),
    )


class AgentMemoryTool(BaseTool):
    name: str = "Agent Memory Access"
    description: str = (
        "Access the BPR&D agent memory system. Read agent profiles for persona "
        "consistency, check active context for work continuity, review learnings "
        "from past sessions, or read shared team resources. "
        "Use agent_name='shared' with memory_type='team_state' to get current priorities."
    )
    args_schema: Type[BaseModel] = MemoryInput

    def _run(self, agent_name: str, memory_type: str) -> str:
        # Map inputs to file paths
        path = self._resolve_path(agent_name.lower(), memory_type.lower())
        if path is None:
            return (
                f"Invalid memory request: agent='{agent_name}', type='{memory_type}'. "
                f"Valid agents: grok, claude, gemini, abacus, shared. "
                f"Valid types: profile, context, learnings, team_state, user_context, protocols."
            )

        # Try filesystem first (local dev), fall back to GitHub API (production)
        local_path = settings.AGENTS_DIR / path
        if local_path.exists():
            try:
                content = local_path.read_text(encoding="utf-8")
                if len(content) > 6000:
                    content = content[:6000] + "\n\n... [truncated]"
                return content
            except Exception as e:
                return f"Error reading local file: {e}"

        # Fall back to GitHub API
        github_path = f"_agents/{path}"
        url = f"{GITHUB_API}/repos/{REPO}/contents/{github_path}"
        try:
            resp = requests.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            if len(content) > 6000:
                content = content[:6000] + "\n\n... [truncated]"
            return content
        except requests.RequestException as e:
            return f"Memory file not found: {github_path} ({e})"

    @staticmethod
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
