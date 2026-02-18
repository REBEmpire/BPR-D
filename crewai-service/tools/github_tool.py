"""
GitHub tools for BPR&D meeting service.
Provides read/write access to repo state during and after meetings.
Supports atomic commits of multiple files via the Git Data API.
"""

import base64
import logging
import re
import asyncio

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


async def list_commits(count: int = 10, branch: str = "main") -> str:
    """List recent commits from the repository."""
    count = min(count, 30)
    url = f"{GITHUB_API}/repos/{REPO}/commits"
    params = {"per_page": count, "sha": branch}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), params=params, timeout=15)
            resp.raise_for_status()
            commits = resp.json()
        except httpx.HTTPError as e:
            return f"Error fetching commits: {e}"

    if not commits:
        return "No commits found."

    lines = []
    for c in commits:
        sha = c["sha"][:7]
        msg = c["commit"]["message"].split("\n")[0]
        date = c["commit"]["author"]["date"][:10]
        author = c["commit"]["author"].get("name", "unknown")
        lines.append(f"- [{sha}] {msg} ({author}, {date})")

    return f"Recent commits on {branch}:\n" + "\n".join(lines)


async def read_file(path: str, branch: str = "main") -> str:
    """Read a file from the GitHub repository."""
    url = f"{GITHUB_API}/repos/{REPO}/contents/{path}"
    params = {"ref": branch}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            return f"Error reading file '{path}': {e}"

    if isinstance(data, list):
        entries = [f"  {'[dir]' if d['type'] == 'dir' else '[file]'} {d['name']}" for d in data]
        return f"Directory listing for '{path}':\n" + "\n".join(entries)

    if data.get("encoding") == "base64" and data.get("content"):
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
            if len(content) > 8000:
                content = content[:8000] + "\n\n... [truncated, file exceeds 8000 chars]"
            return content
        except Exception as e:
            return f"Error decoding file '{path}': {e}"

    return f"File '{path}' exists but could not be decoded."


async def list_handoffs(include_archived: bool = False) -> str:
    """List active task handoffs in the handoff queue."""
    url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_handoffs"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            files = resp.json()
        except httpx.HTTPError as e:
            return f"Error listing handoffs: {e}"

        if not isinstance(files, list):
            return "No handoffs directory found or empty."

        handoff_files = [
            f["name"] for f in files
            if f["name"].endswith(".md") and f["type"] == "file"
        ]

        if not handoff_files:
            return "No active handoffs in the queue."

        summaries = []
        for fname in handoff_files[:10]:
            file_url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_handoffs/{fname}"
            try:
                file_resp = await client.get(file_url, headers=_headers(), timeout=10)
                file_resp.raise_for_status()
                file_data = file_resp.json()
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                summary = content[:500].strip()
                summaries.append(f"### {fname}\n{summary}\n")
            except Exception:
                summaries.append(f"### {fname}\n[Could not read file]\n")

        result = f"Active handoffs ({len(handoff_files)} total):\n\n" + "\n".join(summaries)

        if include_archived:
            archive_url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_handoffs/archive"
            try:
                archive_resp = await client.get(archive_url, headers=_headers(), timeout=10)
                archive_resp.raise_for_status()
                archive_files = archive_resp.json()
                archived_names = [f["name"] for f in archive_files if f["name"].endswith(".md")]
                result += f"\n\nArchived handoffs: {len(archived_names)} completed"
            except Exception:
                result += "\n\nArchive: Could not access."

    return result


async def list_sessions(count: int = 3) -> str:
    """Read the most recent session summaries from _agents/_sessions/.

    Extracts only the Summary section from each file to avoid pulling
    full transcripts into context.
    """
    url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_sessions"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            files = resp.json()
        except httpx.HTTPError as e:
            return f"Error listing sessions: {e}"

        if not isinstance(files, list):
            return "No sessions directory found."

        session_files = sorted(
            [f["name"] for f in files if f["name"].endswith(".md") and f["type"] == "file"],
        )

        # Take the most recent `count` files (sorted by YYYY-MM-DD prefix)
        recent = session_files[-count:] if len(session_files) > count else session_files

        if not recent:
            return "No session files found."

        summaries = []
        for fname in recent:
            file_url = f"{GITHUB_API}/repos/{REPO}/contents/_agents/_sessions/{fname}"
            try:
                file_resp = await client.get(file_url, headers=_headers(), timeout=10)
                file_resp.raise_for_status()
                file_data = file_resp.json()
                content = base64.b64decode(file_data["content"]).decode("utf-8")

                # Extract Summary section only
                summary = _extract_summary(content)
                summaries.append(f"### {fname}\n{summary}\n")
            except Exception:
                summaries.append(f"### {fname}\n[Could not read file]\n")

    return f"Recent sessions ({len(recent)}):\n\n" + "\n".join(summaries)


def _extract_summary(content: str) -> str:
    """Extract the ## Summary section from session markdown.

    Falls back to the first 500 chars if no Summary heading found.
    """
    match = re.search(r"^## Summary\s*\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL)
    if match:
        summary = match.group(1).strip()
        if len(summary) > 2000:
            summary = summary[:2000] + "\n... [truncated]"
        return summary

    # Fallback: return first 500 chars
    return content[:500].strip() + "\n... [no Summary section found]"


async def commit_file(path: str, content: str, message: str, branch: str = "main") -> bool:
    """Commit a file to the GitHub repository. Returns True on success."""
    url = f"{GITHUB_API}/repos/{REPO}/contents/{path}"

    async with httpx.AsyncClient() as client:
        # Check if file exists (need sha for update)
        sha = None
        try:
            resp = await client.get(url, headers=_headers(), params={"ref": branch}, timeout=15)
            if resp.status_code == 200:
                sha = resp.json().get("sha")
        except httpx.HTTPError:
            pass

        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        payload = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        try:
            resp = await client.put(url, headers=_headers(), json=payload, timeout=30)
            resp.raise_for_status()
            logger.info(f"Committed {path} to {branch}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to commit {path}: {e}")
            return False


# --- Git Data API (Atomic Commits) ---

async def get_ref_sha(branch: str = "main") -> str | None:
    """Get the SHA of the latest commit on a branch."""
    url = f"{GITHUB_API}/repos/{REPO}/git/ref/heads/{branch}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            return resp.json()["object"]["sha"]
        except Exception as e:
            logger.error(f"Failed to get ref for {branch}: {e}")
            return None


async def get_commit_tree(sha: str) -> str | None:
    """Get the tree SHA of a commit."""
    url = f"{GITHUB_API}/repos/{REPO}/git/commits/{sha}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=_headers(), timeout=15)
            resp.raise_for_status()
            return resp.json()["tree"]["sha"]
        except Exception as e:
            logger.error(f"Failed to get tree for commit {sha}: {e}")
            return None


async def create_blob(content: str) -> str | None:
    """Create a blob for a file content. Returns blob SHA."""
    url = f"{GITHUB_API}/repos/{REPO}/git/blobs"
    payload = {"content": content, "encoding": "utf-8"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=_headers(), json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json()["sha"]
        except Exception as e:
            logger.error(f"Failed to create blob: {e}")
            return None


async def create_tree(base_tree_sha: str, tree_items: list[dict]) -> str | None:
    """Create a new tree from a base tree and a list of new items."""
    url = f"{GITHUB_API}/repos/{REPO}/git/trees"
    payload = {
        "base_tree": base_tree_sha,
        "tree": tree_items
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=_headers(), json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json()["sha"]
        except Exception as e:
            logger.error(f"Failed to create tree: {e}")
            return None


async def create_commit(message: str, tree_sha: str, parent_sha: str) -> str | None:
    """Create a new commit pointing to a tree and a parent commit."""
    url = f"{GITHUB_API}/repos/{REPO}/git/commits"
    payload = {
        "message": message,
        "tree": tree_sha,
        "parents": [parent_sha]
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=_headers(), json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json()["sha"]
        except Exception as e:
            logger.error(f"Failed to create commit: {e}")
            return None


async def update_ref(branch: str, commit_sha: str) -> bool:
    """Update the branch reference to point to the new commit."""
    url = f"{GITHUB_API}/repos/{REPO}/git/refs/heads/{branch}"
    payload = {"sha": commit_sha, "force": False}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.patch(url, headers=_headers(), json=payload, timeout=15)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update ref {branch}: {e}")
            return False


async def commit_multiple_files(changes: dict[str, str], message: str, branch: str = "main") -> bool:
    """
    Atomically commit multiple files to the repository.

    Args:
        changes: Dict mapping file_path -> file_content.
        message: Commit message.
        branch: Branch to commit to (default: main).

    Returns:
        True if successful, False otherwise.
    """
    logger.info(f"Starting atomic commit of {len(changes)} files to {branch}")

    # 1. Get latest commit SHA
    latest_commit_sha = await get_ref_sha(branch)
    if not latest_commit_sha:
        return False

    # 2. Get the tree of the latest commit
    base_tree_sha = await get_commit_tree(latest_commit_sha)
    if not base_tree_sha:
        return False

    # 3. Create blobs for all files
    tree_items = []
    for path, content in changes.items():
        blob_sha = await create_blob(content)
        if not blob_sha:
            logger.error(f"Failed to create blob for {path}, aborting commit.")
            return False

        tree_items.append({
            "path": path,
            "mode": "100644",  # Standard file mode
            "type": "blob",
            "sha": blob_sha
        })

    # 4. Create a new tree
    new_tree_sha = await create_tree(base_tree_sha, tree_items)
    if not new_tree_sha:
        return False

    # 5. Create a new commit
    new_commit_sha = await create_commit(message, new_tree_sha, latest_commit_sha)
    if not new_commit_sha:
        return False

    # 6. Update the branch reference
    success = await update_ref(branch, new_commit_sha)

    if success:
        logger.info(f"Successfully committed {len(changes)} files. New SHA: {new_commit_sha}")
    else:
        logger.error("Failed to update branch reference.")

    return success
