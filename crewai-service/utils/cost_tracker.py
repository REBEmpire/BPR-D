"""
Cost tracking for BPR&D meetings.
Monitors token usage per agent, enforces budget caps per Grok's directives:
  - Auto-terminate at $1.50/meeting
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

# Cost per 1K tokens (input/output averaged) as of Feb 2026
COST_PER_1K_TOKENS = {
    "grok": 0.005,
    "claude": 0.015,
    "gemini": 0.001,
    "abacus": 0.003,
    "default": 0.005,
}


@dataclass
class AgentUsage:
    """Token usage for a single agent in a meeting."""
    agent_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class CostTracker:
    """Tracks token usage and costs for a single meeting execution."""

    meeting_id: str = ""
    start_time: float = field(default_factory=time.time)
    agent_usage: dict[str, AgentUsage] = field(default_factory=dict)
    terminated_early: bool = False
    termination_reason: str | None = None

    def record_usage(self, agent_name: str, prompt_tokens: int, completion_tokens: int, cost_usd: float = 0.0) -> None:
        """Record token usage for an agent. Uses provided cost if available, else estimates."""
        if agent_name not in self.agent_usage:
            self.agent_usage[agent_name] = AgentUsage(agent_name=agent_name)

        usage = self.agent_usage[agent_name]
        usage.prompt_tokens += prompt_tokens
        usage.completion_tokens += completion_tokens

        if cost_usd > 0:
            usage.cost_usd += cost_usd
        else:
            rate = COST_PER_1K_TOKENS.get(agent_name, COST_PER_1K_TOKENS["default"])
            usage.cost_usd += ((prompt_tokens + completion_tokens) / 1000) * rate

    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.agent_usage.values())

    @property
    def total_prompt_tokens(self) -> int:
        return sum(u.prompt_tokens for u in self.agent_usage.values())

    @property
    def total_completion_tokens(self) -> int:
        return sum(u.completion_tokens for u in self.agent_usage.values())

    @property
    def total_cost(self) -> float:
        return sum(u.cost_usd for u in self.agent_usage.values())

    @property
    def execution_time(self) -> float:
        return time.time() - self.start_time

    def check_budget(self) -> bool:
        """Returns True if within budget, False if should terminate."""
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
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
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
            logger.info(
                f"  {name}: {usage.prompt_tokens}+{usage.completion_tokens} tokens, "
                f"${usage.cost_usd:.4f}"
            )


def get_monthly_cost_breakdown(log_dir: Path | None = None) -> dict:
    """Load monthly spend broken down by agent."""
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "logs"

    if not log_dir.exists():
        return {"total": 0.0, "by_agent": {}}

    current_month = datetime.utcnow().strftime("%Y-%m")
    total = 0.0
    by_agent = {}

    for log_file in log_dir.glob(f"cost-{current_month}*.json"):
        try:
            data = json.loads(log_file.read_text())
            total += data.get("cost_usd", 0.0)

            # Aggregate per agent
            for agent, cost in data.get("by_agent", {}).items():
                by_agent[agent] = by_agent.get(agent, 0.0) + cost

        except Exception:
            continue

    return {
        "total": round(total, 4),
        "by_agent": {k: round(v, 4) for k, v in by_agent.items()}
    }

def load_monthly_spend(log_dir: Path | None = None) -> float:
    """Load cumulative monthly spend from cost log files."""
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
