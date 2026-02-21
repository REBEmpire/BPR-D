"""Meeting-Code-Deployer (MCD) - Automated pipeline for meeting-to-code transformations."""

from .deployer import MeetingCodeDeployer
from .parser import TranscriptParser
from .skill_linker import SkillLinker
from .code_generator import CodeGenerator
from .task_creator import TaskCreator

__version__ = "2.0.0"
__all__ = [
    "MeetingCodeDeployer",
    "TranscriptParser", 
    "SkillLinker",
    "CodeGenerator",
    "TaskCreator",
]
