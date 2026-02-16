"""
Cost tracking for BPR&D CrewAI meetings.
Monitors token usage per agent, enforces budget caps per Grok's directives:
  - Auto-terminate at $0.40/meeting
  - Monthly cap: $20.00
  - Monthly alert: $15.00
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)

# Approximate cost per 1K tokens (input + output averaged) as of Feb 2026
# These are estimates - actual costs depend on input vs output ratio
COST_PER_1K_TOKENS = {
    "grok": 0.005,       # xAI grok-4-1-fast-reasoning
    "claude": 0.015,     # Anthropic claude-sonnet-4-5
    "gemini": 0.001,     # Google gemini-3.0-pro-preview
    "abacus": 0.003,     # Abacus.AI qwen3-max via RouteLLM
    "default": 0.005,
}


@dataclass
class AgentUsage:
    """Token usage for a single agent in a meeting."""
    agent_name: str
    tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class CostTracker:
    """
    Tracks token usage and costs for a single meeting execution.
    Provides budget enforcement per Grok's directives.
    """

    meeting_id: str = ""
    start_time: float = field(default_factory=time.time)
    agent_usage: dict[str, AgentUsage] = field(default_factory=dict)
    terminated_early: bool = False
    termination_reason: str | None = None

    def record_usage(self, agent_name: str, tokens: int) -> None:
        """Record token usage for an agent."""
        rate = COST_PER_1K_TOKENS.get(agent_name, COST_PER_1K_TOKENS["default"])
        cost = (tokens / 1000) * rate

        if agent_name not in self.agent_usage:
            self.agent_usage[agent_name] = AgentUsage(agent_name=agent_name)

        self.agent_usage[agent_name].tokens += tokens
        self.agent_usage[agent_name].cost_usd += cost

    @property
    def total_tokens(self) -> int:
        return sum(u.tokens for u in self.agent_usage.values())

    @property
    def total_cost(self) -> float:
        return sum(u.cost_usd for u in self.agent_usage.values())

    @property
    def execution_time(self) -> float:
        return time.time() - self.start_time

    def check_budget(self) -> bool:
        """
        Check if meeting is within budget.
        Returns True if OK, False if should terminate.
        """
        if self.total_cost >= settings.MEETING_COST_HARD_CAP:
            self.terminated_early = True
            self.termination_reason = (
                f"Meeting cost ${self.total_cost:.2f} exceeded "
                f"hard cap ${settings.MEETING_COST_HARD_CAP:.2f}"
            )
            logger.warning(self.termination_reason)
            return False
        return True

    def to_dict(self) -> dict:
        """Export cost data for the MeetingResponse."""
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": 0,  # Detailed breakdown requires callback integration
            "completion_tokens": 0,
            "cost_usd": round(self.total_cost, 4),
            "by_agent": {
                name: round(usage.cost_usd, 4)
                for name, usage in self.agent_usage.items()
            },
            "execution_time_seconds": round(self.execution_time, 1),
            "terminated_early": self.terminated_early,
            "termination_reason": self.termination_reason,
        }

    def log_summary(self) -> None:
        """Log a human-readable cost summary."""
        logger.info(
            f"Meeting {self.meeting_id} cost summary: "
            f"${self.total_cost:.4f} total, "
            f"{self.total_tokens} tokens, "
            f"{self.execution_time:.1f}s"
        )
        for name, usage in self.agent_usage.items():
            logger.info(f"  {name}: {usage.tokens} tokens, ${usage.cost_usd:.4f}")


def load_monthly_spend(log_dir: Path | None = None) -> float:
    """
    Load cumulative monthly spend from cost log files.
    Returns total USD spent this month.
    """
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "logs"

    if not log_dir.exists():
        return 0.0

    current_month = datetime.utcnow().strftime("%Y-%m")
    total = 0.0

    for log_file in log_dir.glob(f"cost-{current_month}*.json"):
        try:
            data = json.loads(log_file.read_text())
            total += data.get("cost_usd", 0.0)
        except Exception:
            continue

    return total


def save_cost_log(tracker: CostTracker, log_dir: Path | None = None) -> None:
    """Save cost data to a log file for monthly tracking."""
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "logs"

    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    log_file = log_dir / f"cost-{timestamp}-{tracker.meeting_id}.json"

    data = tracker.to_dict()
    data["meeting_id"] = tracker.meeting_id
    data["timestamp"] = datetime.utcnow().isoformat()

    log_file.write_text(json.dumps(data, indent=2))
    logger.info(f"Cost log saved: {log_file}")
