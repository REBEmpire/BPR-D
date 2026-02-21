"""
API Healer: Dynamic model discovery, fallback, and retry logic for LLM calls.
Created by Gemini/Russell/Grok/Claude based on handoff specs.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Callable, List, Optional

import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

class APIHealer:
    def __init__(self):
        self.log_dir = "_agents/_logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(
            self.log_dir, f"api_healer_{datetime.now().strftime('%Y%m%d')}.json"
        )

        # Configure genai if key is available
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        else:
            logger.warning("GEMINI_API_KEY not set. APIHealer functionality limited.")

        self.available_models = self._discover_models()
        self.fallback_chain = self._build_fallback_chain()

    def _discover_models(self) -> List[str]:
        """Query Gemini API for available models."""
        try:
            # In a real environment, query genai.list_models()
            # For now, return a default list if SDK fails or key is missing
            models = []
            if settings.GEMINI_API_KEY:
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            models.append(m.name)
                except Exception as e:
                    logger.warning(f"Failed to list models: {e}")

            if not models:
                # Fallback to hardcoded list if discovery fails
                models = [
                    "models/gemini-3.1-pro-preview",
                    "models/gemini-3.1-flash-preview",
                    "models/gemini-3.0-pro-preview",
                    "models/gemini-3.0-flash-preview",
                    "models/gemini-2.0-flash-exp",
                    "models/gemini-1.5-pro",
                    "models/gemini-1.5-flash",
                    "models/gemini-1.0-pro"
                ]
            return models
        except Exception as e:
            logger.error(f"Error discovering models: {e}")
            # Ensure even in error case we try the best models first
            return ["models/gemini-3.1-pro-preview", "models/gemini-1.5-pro"]

    def _build_fallback_chain(self) -> List[str]:
        """Order models by reliability: stable -> preview -> experimental."""
        # Preference order (Updated for 3.1/3.0 priority)
        priority = [
            "gemini-3.1-pro",
            "gemini-3.0-pro",
            "gemini-3.1-flash",
            "gemini-3.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.0-pro"
        ]

        chain = []
        for p in priority:
            for m in self.available_models:
                if p in m:
                    chain.append(m)

        # Add remaining models
        for m in self.available_models:
            if m not in chain:
                chain.append(m)

        # Remove duplicates
        return list(dict.fromkeys(chain))

    async def heal_async(self, func: Callable[[str], Any], *args, **kwargs) -> Any:
        """
        Execute an async function with retry logic and model fallback.

        Args:
            func: The async function to execute. It must accept 'model' as a keyword argument.
            *args, **kwargs: Arguments to pass to func.
        """
        last_error = None

        for model in self.fallback_chain:
            # Retry logic per model
            for attempt in range(3):
                try:
                    # Execute the function with the specific model
                    response = await func(*args, model=model, **kwargs)
                    self.log_attempt("unknown", model, success=True)
                    return response
                except Exception as e:
                    last_error = e
                    self.log_attempt("unknown", model, success=False, error=str(e))
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Attempt {attempt+1} failed with model {model}: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

            logger.warning(f"All attempts failed for model {model}. Trying next model in chain.")

        raise Exception(f"All models failed. Last error: {last_error}")

    def log_attempt(self, agent: str, model: str, success: bool, error: str = None):
        """Log to JSON file for analysis."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "success": success,
            "error": error
        }

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log attempt: {e}")

    def health_check(self) -> dict:
        """Simple health check returning available models and chain."""
        return {
            "status": "active",
            "models_discovered": len(self.available_models),
            "fallback_chain": self.fallback_chain
        }
