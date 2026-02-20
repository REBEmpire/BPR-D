import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# --- Shim for missing dependencies ---
# This allows running the tests in an environment where the actual
# dependencies (fastapi, pydantic, openai, etc.) are not installed.
mock_modules = [
    "dotenv", "pydantic", "fastapi", "fastapi.middleware.cors",
    "openai", "anthropic", "google", "google.generativeai", "httpx",
    "apscheduler", "apscheduler.schedulers.asyncio", "apscheduler.triggers.cron"
]
for mod in mock_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Mock settings to avoid dotenv issues
class MockSettings:
    def __init__(self):
        self.XAI_API_KEY = "test_key"
        self.ANTHROPIC_API_KEY = "test_key"
        self.GEMINI_API_KEY = "test_key"
        self.GITHUB_TOKEN = "test_token"
        self.GITHUB_REPO = "REBEmpire/BPR-D"  # Match expected value in test_config.py
        self.AGENTS_DIR = Path(__file__).parent.parent.parent / "_agents"
        self.ENV = "testing"
        self.LOG_LEVEL = "INFO"
        self.ABACUS_PRIMARY_KEY = "test_key"
        self.ABACUS_BACKUP_KEY = ""
        self.BPRD_API_KEY = "test_key"

# We need to inject the mock settings before importing anything that uses it
if 'config' not in sys.modules:
    mock_config = MagicMock()
    mock_config.settings = MockSettings()
    sys.modules['config'] = mock_config

# --- End Shim ---

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Now we can safely import our modules
from agents.persona import load_persona
from agents.registry import resolve_participants

class TestAgents(unittest.IsolatedAsyncioTestCase):
    # --- Persona Tests ---
    async def test_grok_persona_loading(self):
        persona = await load_persona("grok")
        self.assertIsNotNone(persona)
        self.assertEqual(persona.name, "grok")
        self.assertIn("CHIEF", persona.meeting_role)

    async def test_claude_persona_loading(self):
        persona = await load_persona("claude")
        self.assertIsNotNone(persona)
        self.assertIn("CHIEF STRATEGIST", persona.meeting_role)

    async def test_gemini_persona_loading(self):
        persona = await load_persona("gemini")
        self.assertIsNotNone(persona)
        self.assertIn("LEAD DEVELOPER", persona.meeting_role)

    async def test_abacus_persona_loading(self):
        persona = await load_persona("abacus")
        self.assertIsNotNone(persona)
        self.assertIn("CHIEF INNOVATOR", persona.meeting_role)

    async def test_unknown_agent(self):
        persona = await load_persona("unknown")
        self.assertIsNone(persona)

    # --- Registry Tests ---
    def test_resolve_participants_default(self):
        with patch('agents.registry.is_abacus_available', return_value=True):
            participants = resolve_participants(None, "team_meeting")
            self.assertEqual(len(participants), 4)
            self.assertIn("abacus", participants)
            self.assertIn("grok", participants)

    def test_resolve_participants_explicit(self):
        participants = resolve_participants(["grok", "claude"], "team_meeting")
        self.assertEqual(participants, ["grok", "claude"])

    def test_resolve_participants_abacus_unavailable(self):
        with patch('agents.registry.is_abacus_available', return_value=False):
            # Abacus should be filtered out if requested but unavailable
            participants = resolve_participants(["grok", "abacus"], "team_meeting")
            self.assertEqual(participants, ["grok"])

            # Abacus should not be in default if unavailable
            participants = resolve_participants(None, "team_meeting")
            self.assertNotIn("abacus", participants)
            self.assertEqual(len(participants), 3)

if __name__ == '__main__':
    unittest.main()
