#!/usr/bin/env python3
"""
Meeting Secretary Bot — Main Orchestrator
==========================================
Triggered by GitHub Actions when a new session file is committed to _agents/_sessions/.
Reads the session file, parses structured meeting data, and fans out updates to:
  1. BPR&D_To_Do_List.md
  2. _agents/{agent}/handoff.md (per agent)
  3. tasks/projects/{task_id}.md (for large handoffs)
  4. _agents/{agent}/context/active.md (delta update)

Usage:
  python secretary.py _agents/_sessions/2026-02-19-daily-briefing.md
"""

import sys
import os
import logging
from pathlib import Path

# Add pipeline root to path
sys.path.insert(0, str(Path(__file__).parent))

from parser import parse_session_file
from updaters.todo_updater import update_todo_list
from updaters.handoff_updater import update_handoffs
from updaters.project_creator import create_project_files
from updaters.active_updater import update_active_contexts

logging.basicConfig(
    level=logging.INFO,
    format="[SecretaryBot] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        logger.error("Usage: secretary.py <session_file_path>")
        sys.exit(1)

    session_file = sys.argv[1]

    if not os.path.exists(session_file):
        logger.error(f"Session file not found: {session_file}")
        sys.exit(1)

    # Ensure we're running from repo root
    repo_root = _find_repo_root(session_file)
    if repo_root:
        os.chdir(repo_root)
        logger.info(f"Working directory: {repo_root}")

    logger.info(f"Processing session file: {session_file}")
    logger.info("=" * 60)

    # Step 1: Parse session file
    logger.info("Step 1/4: Parsing session file...")
    meeting_data = parse_session_file(session_file)

    action_count = len(meeting_data.get("action_items", []))
    handoff_count = len(meeting_data.get("handoffs", []))
    logger.info(f"  Parsed: {action_count} action items, {handoff_count} handoffs")
    logger.info(f"  Session: {meeting_data.get('session_type')} | {meeting_data.get('session_date')}")

    if action_count == 0 and handoff_count == 0:
        logger.info("No action items or handoffs found in session. Nothing to update.")
        return

    # Step 2: Update To-Do list
    logger.info("Step 2/4: Updating BPR&D_To_Do_List.md...")
    todo_added = update_todo_list(meeting_data)
    logger.info(f"  Added {todo_added} item(s) to To-Do list")

    # Step 3: Update agent handoffs
    logger.info("Step 3/4: Updating agent handoff files...")
    handoff_counts = update_handoffs(meeting_data)
    for agent, count in handoff_counts.items():
        logger.info(f"  [{agent}] Added {count} task(s)")
    if not handoff_counts:
        logger.info("  No handoff updates needed")

    # Step 4a: Create project files for large handoffs
    logger.info("Step 4a/4: Creating tasks/projects/ files for large handoffs...")
    projects_created = create_project_files(meeting_data)
    logger.info(f"  Created {projects_created} project file(s)")

    # Step 4b: Update agent active.md contexts
    logger.info("Step 4b/4: Updating agent active.md contexts...")
    active_results = update_active_contexts(meeting_data)
    for agent, updated in active_results.items():
        status = "updated" if updated else "skipped"
        logger.info(f"  [{agent}] active.md {status}")

    # Summary
    logger.info("=" * 60)
    logger.info("Secretary Bot complete!")
    logger.info(f"  To-Do items added:    {todo_added}")
    logger.info(f"  Handoff rows added:   {sum(handoff_counts.values())}")
    logger.info(f"  Project files created:{projects_created}")
    logger.info(f"  Active.md updated:    {sum(1 for v in active_results.values() if v)}")
    logger.info("GitHub Actions will commit these changes.")


def _find_repo_root(session_file: str) -> str | None:
    """Walk up from session file to find the git repo root."""
    path = Path(session_file).resolve()
    for parent in [path] + list(path.parents):
        if (parent / ".git").exists():
            return str(parent)
    # Fallback: current working directory
    return None


if __name__ == "__main__":
    main()
