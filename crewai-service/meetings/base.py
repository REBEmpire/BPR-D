"""
Base meeting type for BPR&D meeting service.
Defines the interface all meeting types implement.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from agents.registry import RegisteredAgent
from models.meeting import MeetingResponse
from orchestrator.transcript import Transcript
from utils.cost_tracker import CostTracker


class BaseMeeting(ABC):
    """Abstract base for all meeting types."""

    meeting_type: str

    @abstractmethod
    async def execute(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
    ) -> MeetingResponse:
        """Execute the meeting and return a structured response."""
        ...

    async def stream(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
    ) -> AsyncGenerator[dict, None]:
        """Execute the meeting and yield events for SSE."""
        # Default implementation for non-streaming meetings (can be overridden)
        yield {"type": "error", "error": "Streaming not implemented for this meeting type"}
