#!/usr/bin/env python3
"""
Meeting Secretary Bot — Main Orchestrator
==========================================
Triggered by GitHub Actions when a new session file is committed to _agents/_sessions/.
Reads the session file, parses structured meeting data, and fans out updates to:
  1. BPR&D_To_Do_List.md
  2. tasks/projects/{task_id}.md (for large handoffs)
  3. _staging/pending_commits.json (ship-to-repo blocks via meeting_code_deployer)

Document Generation Ownership (to prevent duplicate generation):
  - BPR&D_To_Do_List.md: secretary.py via todo_updater (ONLY HERE)
  - tasks/projects/*.md: secretary.py via project_creator (ONLY HERE)
  - _staging/pending_commits.json: meeting_code_deployer (ONLY THERE)

DEPRECATED (orchestrator owns these files):
  - _agents/{agent}/handoff.md (removed - handoff system deprecated)
  - _agents/{agent}/context/active.md (removed - orchestrator owns)

Usage:
  python secretary.py _agents/_sessions/2026-02-19-daily-briefing.md
"""

import sys
import os
import logging
from pathlib import Path

# Add pipeline root to path
sys.path.insert(0, str(Path(__file__).parent))

# Add repo root to path for _agents module access
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT_PATH = SCRIPT_DIR.parent.parent.parent  # pipelines/github-bot/meeting-parser -> repo root
sys.path.insert(0, str(REPO_ROOT_PATH))

from parser import parse_session_file
from updaters.todo_updater import update_todo_list
# DEPRECATED: from updaters.handoff_updater import update_handoffs
from updaters.project_creator import create_project_files
# DEPRECATED: from updaters.active_updater import update_active_contexts

# Import from integrated meeting_code_deployer (replaces standalone ship_to_repo_parser)
from _agents.meeting_code_deployer import parse_ship_to_repo_blocks, write_pending_commits

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

    # Step 2: Update To-Do list
    logger.info("Step 2/4: Updating BPR&D_To_Do_List.md...")
    todo_added = update_todo_list(meeting_data)
    logger.info(f"  Added {todo_added} item(s) to To-Do list")

    # Step 3: DEPRECATED - handoff system removed
    # Handoffs are now managed by orchestrator directly
    # logger.info("Step 3/4: Updating agent handoff files...")
    # handoff_counts = update_handoffs(meeting_data)
    logger.info("Step 3/4: Handoff system deprecated - skipping")

    # Step 4a: Create project files for large handoffs
    logger.info("Step 4a/4: Creating tasks/projects/ files for large handoffs...")
    projects_created = create_project_files(meeting_data)
    logger.info(f"  Created {projects_created} project file(s)")

    # Step 4b: DEPRECATED - active.md owned by orchestrator
    # logger.info("Step 4b/4: Updating agent active.md contexts...")
    # active_results = update_active_contexts(meeting_data)
    logger.info("Step 4b/4: active.md updates deprecated - orchestrator owns these files")

    # Step 5: Parse ship-to-repo blocks and write to staging
    logger.info("Step 5/4: Parsing ship-to-repo blocks from session...")
    with open(session_file, encoding="utf-8") as f:
        session_content = f.read()
    
    ship_blocks = parse_ship_to_repo_blocks(session_content, session_file)
    if ship_blocks:
        staging_path = write_pending_commits(ship_blocks, repo_root or ".")
        logger.info(f"  Queued {len(ship_blocks)} file(s) for ship-to-repo")
        logger.info(f"  Staging file: {staging_path}")
    else:
        logger.info("  No ship-to-repo blocks found")

    # Summary
    logger.info("=" * 60)
    logger.info("Secretary Bot complete!")
    logger.info(f"  To-Do items added:    {todo_added}")
    logger.info(f"  Project files created:{projects_created}")
    logger.info(f"  Ship-to-repo queued:  {len(ship_blocks) if ship_blocks else 0}")
    logger.info("GitHub Actions will process pending commits.")


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
