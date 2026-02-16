"""
GitHub Tools for BPR&D CrewAI agents.
Provides read access to repo state during meetings: commits, files, handoffs.
Write operations (commit notes, create handoffs) are handled by n8n post-meeting.

Priority: Phase 1 tool per Grok's directive.
"""

import base64
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config import settings


GITHUB_API = "https://api.github.com"
REPO = settings.GITHUB_REPO  # REBEmpire/BPR-D


def _headers() -> dict:
    return {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


# --- List Recent Commits ---

class ListCommitsInput(BaseModel):
    count: int = Field(
        default=10,
        description="Number of recent commits to return (max 30).",
    )
    branch: str = Field(
        default="main",
        description="Branch to list commits from.",
    )


class GitHubListCommitsTool(BaseTool):
    name: str = "List Recent GitHub Commits"
    description: str = (
        "Lists recent commits to the BPR&D repository. "
        "Use this to review what's been shipped since the last meeting, "
        "track progress on action items, and identify active contributors."
    )
    args_schema: Type[BaseModel] = ListCommitsInput

    def _run(self, count: int = 10, branch: str = "main") -> str:
        count = min(count, 30)
        url = f"{GITHUB_API}/repos/{REPO}/commits"
        params = {"per_page": count, "sha": branch}

        try:
            resp = requests.get(url, headers=_headers(), params=params, timeout=15)
            resp.raise_for_status()
            commits = resp.json()
        except requests.RequestException as e:
            return f"Error fetching commits: {e}"

        if not commits:
            return "No commits found."

        lines = []
        for c in commits:
            sha = c["sha"][:7]
            msg = c["commit"]["message"].split("\n")[0]  # First line only
            date = c["commit"]["author"]["date"][:10]
            author = c["commit"]["author"].get("name", "unknown")
            lines.append(f"- [{sha}] {msg} ({author}, {date})")

        return f"Recent commits on {branch}:\n" + "\n".join(lines)


# --- Read File ---

class ReadFileInput(BaseModel):
    path: str = Field(
        description=(
            "File path within the repository. Examples: "
            "'_agents/team_state.md', '_agents/_protocols.md', "
            "'.bprd/agents.yaml', 'research/topic/brief.md'"
        ),
    )
    branch: str = Field(
        default="main",
        description="Branch to read from.",
    )


class GitHubReadTool(BaseTool):
    name: str = "Read GitHub File"
    description: str = (
        "Reads a file from the BPR&D GitHub repository. "
        "Use this to check team state, agent profiles, protocols, "
        "research briefs, or any other project file. "
        "Returns the file contents as text."
    )
    args_schema: Type[BaseModel] = ReadFileInput

    def _run(self, path: str, branch: str = "main") -> str:
        url = f"{GITHUB_API}/repos/{REPO}/contents/{path}"
        params = {"ref": branch}

        try:
            resp = requests.get(url, headers=_headers(), params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            return f"Error reading file '{path}': {e}"

        if isinstance(data, list):
            # It's a directory listing
            entries = [f"  {'[dir]' if d['type'] == 'dir' else '[file]'} {d['name']}" for d in data]
            return f"Directory listing for '{path}':\n" + "\n".join(entries)

        if data.get("encoding") == "base64" and data.get("content"):
            try:
                content = base64.b64decode(data["content"]).decode("utf-8")
                # Truncate very large files to avoid context window issues
                if len(content) > 8000:
                    content = content[:8000] + "\n\n... [truncated, file exceeds 8000 chars]"
                return content
            except Exception as e:
                return f"Error decoding file '{path}': {e}"

        return f"File '{path}' exists but could not be decoded."


# --- List Handoffs ---

class ListHandoffsInput(BaseModel):
    include_archived: bool = Field(
        default=False,
        description="Whether to include archived/completed handoffs.",
    )


class GitHubListHandoffsTool(BaseTool):
    name: str = "List Active Handoffs"
    description: str = (
        "Lists active task handoffs in the BPR&D handoff queue. "
        "Use this to check what tasks are assigned, who owns them, "
        "and which ones are overdue or blocked. "
        "This is critical for accountability and follow-up."
    )
    args_schema: Type[BaseModel] = ListHandoffsInput

    def _run(self, include_archived: bool = False) -> str:
        # List active handoffs
        url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_handoffs"
        try:
            resp = requests.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            files = resp.json()
        except requests.RequestException as e:
            return f"Error listing handoffs: {e}"

        if not isinstance(files, list):
            return "No handoffs directory found or empty."

        handoff_files = [
            f["name"] for f in files
            if f["name"].endswith(".md") and f["type"] == "file"
        ]

        if not handoff_files:
            return "No active handoffs in the queue."

        # Read each handoff file for summary
        summaries = []
        for fname in handoff_files[:10]:  # Cap at 10 to avoid excessive API calls
            file_url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_handoffs/{fname}"
            try:
                file_resp = requests.get(file_url, headers=_headers(), timeout=10)
                file_resp.raise_for_status()
                file_data = file_resp.json()
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                # Extract first 500 chars as summary
                summary = content[:500].strip()
                summaries.append(f"### {fname}\n{summary}\n")
            except Exception:
                summaries.append(f"### {fname}\n[Could not read file]\n")

        result = f"Active handoffs ({len(handoff_files)} total):\n\n" + "\n".join(summaries)

        if include_archived:
            archive_url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_handoffs/archive"
            try:
                archive_resp = requests.get(archive_url, headers=_headers(), timeout=10)
                archive_resp.raise_for_status()
                archive_files = archive_resp.json()
                archived_names = [f["name"] for f in archive_files if f["name"].endswith(".md")]
                result += f"\n\nArchived handoffs: {len(archived_names)} completed"
            except Exception:
                result += "\n\nArchive: Could not access."

        return result
