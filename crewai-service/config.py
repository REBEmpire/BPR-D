"""
BPR&D CrewAI Service Configuration
Loads environment variables and provides typed access to all settings.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root (one level up from crewai-service/)
PROJECT_ROOT = Path(__file__).parent.parent
AGENTS_DIR = PROJECT_ROOT / "_agents"
BPRD_CONFIG = PROJECT_ROOT / ".bprd"


@dataclass
class Settings:
    """All configuration for the CrewAI service."""

    # --- LLM API Keys ---
    XAI_API_KEY: str = field(default_factory=lambda: os.getenv("XAI_API_KEY", ""))
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    ABACUS_PRIMARY_KEY: str = field(default_factory=lambda: os.getenv("ABACUS_PRIMARY_KEY", ""))
    ABACUS_BACKUP_KEY: str = field(default_factory=lambda: os.getenv("ABACUS_BACKUP_KEY", ""))

    # --- GitHub ---
    GITHUB_TOKEN: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    GITHUB_REPO: str = field(default_factory=lambda: os.getenv("GITHUB_REPO", "REBEmpire/BPR-D"))

    # --- Service ---
    PORT: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # --- Cost Controls (Grok's directives) ---
    MEETING_COST_HARD_CAP: float = 0.40  # Auto-terminate at $0.40/meeting
    MONTHLY_BUDGET_CAP: float = 20.00
    MONTHLY_BUDGET_ALERT: float = 15.00

    # --- CrewAI Defaults ---
    DEFAULT_MAX_ITER: int = 12  # Grok's directive: enough for 2 full debate cycles
    DEFAULT_MAX_RPM: int = 30
    MEETING_TIMEOUT_SECONDS: int = 900  # 15-minute hard timeout

    # --- Paths ---
    AGENTS_YAML: Path = field(default_factory=lambda: BPRD_CONFIG / "agents.yaml")
    AGENTS_DIR: Path = field(default_factory=lambda: AGENTS_DIR)

    def validate(self) -> list[str]:
        """Check that required keys are set. Returns list of missing keys."""
        missing = []
        if not self.XAI_API_KEY:
            missing.append("XAI_API_KEY")
        if not self.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not self.GITHUB_TOKEN:
            missing.append("GITHUB_TOKEN")
        return missing


settings = Settings()
