import sys
import os
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock

# Add crewai-service to path
sys.path.insert(0, os.path.abspath("crewai-service"))

# 1. MOCK MODULES BEFORE IMPORT
# Mock 'google' package
mock_google = MagicMock()
sys.modules["google"] = mock_google
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

# Mock 'config' module
mock_settings = MagicMock()
mock_settings.GEMINI_API_KEY = "fake-key"
mock_settings.XAI_API_KEY = "fake-key"
mock_settings.ANTHROPIC_API_KEY = "fake-key"
mock_settings.ABACUS_PRIMARY_KEY = "fake-key"
mock_config_module = MagicMock()
mock_config_module.settings = mock_settings
sys.modules["config"] = mock_config_module

# Mock 'tools.github_tool' module
mock_github_tool = MagicMock()
async def mock_commit_file(*args, **kwargs):
    print(f"Mock commit_file called with: {args} {kwargs}")
    return True

mock_github_tool.commit_file = mock_commit_file
sys.modules["tools"] = MagicMock()
sys.modules["tools.github_tool"] = mock_github_tool

# 2. IMPORT API_HEALER
try:
    from api_healer import APIHealer
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

async def test_healer_logic():
    print("Testing APIHealer logic...")

    # Instantiate Healer
    healer = APIHealer()
    print(f"Healer instantiated. Flush threshold: {healer.flush_threshold}")

    # Log 15 items (threshold is 10)
    print("Logging 15 attempts...")
    for i in range(15):
        healer.log_attempt("agent", "model", True, f"test {i}")
        await asyncio.sleep(0.01)

    # Wait for background tasks
    await asyncio.sleep(0.5)

    # Verify buffer status
    print(f"Buffer size after flush: {len(healer.log_buffer)}")

    # Verify health check
    health = healer.health_check()
    print(f"Health Check: {json.dumps(health, indent=2)}")

    # Validate provider status
    providers = health.get("providers", {})
    if all(status == "active" for status in providers.values()):
        print("\nAPI Healer Deployment Verification: PASSED")
    else:
        print("\nAPI Healer Deployment Verification: FAILED (Provider status check)")

if __name__ == "__main__":
    asyncio.run(test_healer_logic())
