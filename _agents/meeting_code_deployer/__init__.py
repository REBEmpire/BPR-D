"""Meeting-Code-Deployer (MCD) - Automated pipeline for meeting-to-code transformations.

Includes integrated ship-to-repo functionality for secure code deployment from meetings.
"""

from .deployer import MeetingCodeDeployer
from .parser import (
    TranscriptParser,
    # Ship-to-repo functions (integrated from ship_to_repo_parser.py)
    parse_ship_to_repo_blocks,
    write_pending_commits,
    clear_pending_commits,
)
from .skill_linker import SkillLinker
from .code_generator import CodeGenerator
from .task_creator import TaskCreator

__version__ = "2.1.0"
__all__ = [
    "MeetingCodeDeployer",
    "TranscriptParser", 
    "SkillLinker",
    "CodeGenerator",
    "TaskCreator",
    # Ship-to-repo exports
    "parse_ship_to_repo_blocks",
    "write_pending_commits",
    "clear_pending_commits",
]
