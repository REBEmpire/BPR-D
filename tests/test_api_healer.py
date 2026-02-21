import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies before import
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["config"] = MagicMock()
sys.modules["tools"] = MagicMock()
sys.modules["tools.github_tool"] = MagicMock()

# Manually add the path to import api_healer
sys.path.append("crewai-service")

# Import the module under test
# We use importlib to handle the path properly if needed, but append should work
try:
    import api_healer
except ImportError:
    # If direct import fails due to path issues
    import importlib.util
    spec = importlib.util.spec_from_file_location("api_healer", "crewai-service/api_healer.py")
    api_healer = importlib.util.module_from_spec(spec)
    sys.modules["api_healer"] = api_healer
    spec.loader.exec_module(api_healer)

class TestAPIHealer(unittest.TestCase):
    def setUp(self):
        self.healer = api_healer.APIHealer()

    def test_initialization(self):
        """Test that APIHealer initializes correctly."""
        self.assertIsInstance(self.healer.log_buffer, list)
        self.assertIsInstance(self.healer.available_models, list)
        self.assertIsInstance(self.healer.fallback_chain, list)

    def test_discover_models_fallback(self):
        """Test that model discovery falls back to default list when API fails."""
        # The mock should return empty list or fail, triggering fallback
        models = self.healer._discover_models()
        self.assertTrue(len(models) > 0)
        self.assertIn("models/gemini-1.5-pro", models)

    def test_fallback_chain_construction(self):
        """Test that fallback chain is constructed correctly."""
        chain = self.healer._build_fallback_chain()
        self.assertTrue(len(chain) > 0)
        # Check for unique items
        self.assertEqual(len(chain), len(set(chain)))

    @patch("api_healer.APIHealer.log_attempt")
    async def test_heal_async_success(self, mock_log):
        """Test successful execution of heal_async."""
        async def mock_func(model=None):
            return "success"

        # Since heal_async is async, we need to run it in an event loop or use unittest.IsolatedAsyncioTestCase
        # But for simplicity in this environment, let's just run it if possible or mock the execution.
        # Actually, standard unittest doesn't support async test methods directly without IsolatedAsyncioTestCase (Py3.8+)

        # Let's try to just run it with asyncio.run if available
        import asyncio
        result = await self.healer.heal_async(mock_func)
        self.assertEqual(result, "success")
        mock_log.assert_called_with("unknown", self.healer.fallback_chain[0], success=True)

# Use IsolatedAsyncioTestCase if available
if hasattr(unittest, "IsolatedAsyncioTestCase"):
    class TestAPIHealerAsync(unittest.IsolatedAsyncioTestCase):
        async def asyncSetUp(self):
            self.healer = api_healer.APIHealer()

        @patch("api_healer.APIHealer.log_attempt")
        async def test_heal_async_success(self, mock_log):
            async def mock_func(model=None, **kwargs):
                return "success"

            result = await self.healer.heal_async(mock_func)
            self.assertEqual(result, "success")
            # The first model in fallback chain is used
            mock_log.assert_called()

if __name__ == "__main__":
    unittest.main()
