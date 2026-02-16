"""
Data models for BPR&D meeting requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MeetingType(str, Enum):
    DAILY_BRIEFING = "daily_briefing"
    PROJECT_SYNC = "project_sync"
    RETROSPECTIVE = "retrospective"
    AD_HOC = "ad_hoc"


class MeetingRequest(BaseModel):
    """Incoming request to execute a meeting."""

    meeting_type: MeetingType
    agenda: Optional[str] = Field(
        default=None,
        description="Optional focus topic or agenda items for the meeting.",
    )
    participants: Optional[list[str]] = Field(
        default=None,
        description=(
            "Override default participant list. "
            "Defaults: daily_briefing=['grok','claude','gemini']. "
            "Abacus auto-included when available (after Feb 23)."
        ),
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Optional metadata (trigger source, request ID, etc.).",
    )


class HandoffItem(BaseModel):
    """A task handoff created during the meeting."""

    task_id: str = Field(description="Unique identifier")
    assigned_to: str = Field(description="Agent name or russell")
    title: str = Field(description="Clear, concise task title")
    due_date: Optional[str] = Field(default=None, description="ISO date string")
    priority: str = Field(default="medium", description="low, medium, high, critical")
    context: str = Field(description="Why this task exists and what prompted it")
    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    status: str = Field(default="open")
    created_by: str = Field(default="grok")


class ActionItem(BaseModel):
    """An action item assigned during the meeting."""

    task: str = Field(description="What needs to be done")
    assigned_to: str = Field(description="Who is responsible")
    priority: str = Field(default="medium")
    deadline: Optional[str] = Field(default=None, description="When it's due")


class CostEstimate(BaseModel):
    """Token usage and cost breakdown for a meeting execution."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    by_agent: dict[str, float] = Field(default_factory=dict)
    execution_time_seconds: float = 0.0
    terminated_early: bool = False
    termination_reason: Optional[str] = None


class MeetingResponse(BaseModel):
    """Response returned after meeting execution."""

    success: bool
    meeting_id: str = Field(description="Unique meeting identifier")
    meeting_type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    notes: str = Field(description="Full meeting notes formatted as markdown")
    handoffs: list[HandoffItem] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)
    cost_estimate: CostEstimate = Field(default_factory=CostEstimate)
    error: Optional[str] = Field(default=None, description="Error message if success=False")
