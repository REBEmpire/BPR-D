import unittest
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

# Shim
mock_modules = [
    "dotenv", "pydantic", "fastapi", "fastapi.middleware.cors",
    "openai", "anthropic", "google", "google.generativeai", "httpx",
    "apscheduler", "apscheduler.schedulers.asyncio", "apscheduler.triggers.cron"
]
for mod in mock_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Mock settings
if 'config' not in sys.modules:
    mock_config = MagicMock()
    sys.modules['config'] = mock_config

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "crewai-service"))

# Import the script module
import generate_research_briefs

class TestGenerateBriefs(unittest.IsolatedAsyncioTestCase):
    async def test_generate_brief_mock(self):
        mock_agent = MagicMock()
        mock_agent.provider.generate = AsyncMock(return_value="# Mock Brief")
        mock_agent.persona.build_system_prompt.return_value = "System Prompt"

        # Mock file writing to avoid creating files
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                 with patch("pathlib.Path.exists", return_value=False):
                    await generate_research_briefs.generate_brief(mock_agent, "test-category")

        mock_agent.provider.generate.assert_called_once()
        mock_file().write.assert_called_with("# Mock Brief")

if __name__ == '__main__':
    unittest.main()
