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
from tools.github_tool import commit_file

logger = logging.getLogger(__name__)

class APIHealer:
    def __init__(self):
        # In-memory buffer for logs (flushed to GitHub)
        self.log_buffer: List[dict] = []
        self.flush_threshold = 10
        self.last_flush_time = datetime.now()

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
        """Log to stdout (Render logs) and buffer for GitHub archive."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "success": success,
            "error": error
        }

        # 1. Log to stdout for real-time monitoring
        print(json.dumps(entry))

        # 2. Add to buffer
        self.log_buffer.append(entry)

        # Trigger flush if buffer gets too large
        if len(self.log_buffer) >= self.flush_threshold:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._flush_logs_to_github())
            except RuntimeError:
                pass

    async def _flush_logs_to_github(self):
        """Commit buffered logs to GitHub."""
        if not self.log_buffer:
            return

        # Snapshot and clear buffer
        logs_to_commit = list(self.log_buffer)
        self.log_buffer.clear()

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%H%M%S")

        # Create a unique file for this batch to avoid race conditions
        # Path: meetings/logs/api_health/{date}/batch-{timestamp}.json
        path = f"meetings/logs/api_health/{date_str}/batch-{timestamp}.json"
        content = "\n".join(json.dumps(entry) for entry in logs_to_commit)

        logger.info(f"Flushing {len(logs_to_commit)} API logs to {path}")
        success = await commit_file(
            path=path,
            content=content,
            message=f"API Healer Logs Batch {timestamp}"
        )

        if success:
            self.last_flush_time = now
        else:
            logger.error(f"Failed to flush logs to {path}.")

    def _check_provider_status(self) -> dict:
        """Check status of all known providers based on configuration."""
        status = {
            "gemini": "active" if settings.GEMINI_API_KEY else "missing_key",
            "grok": "active" if settings.XAI_API_KEY else "missing_key",
            "claude": "active" if settings.ANTHROPIC_API_KEY else "missing_key",
            "abacus": "active" if (settings.ABACUS_PRIMARY_KEY or settings.ABACUS_BACKUP_KEY or "809e") else "missing_key"
        }
        return status

    def health_check(self) -> dict:
        """Comprehensive health check returning available models, chain, and provider status."""
        return {
            "status": "active",
            "providers": self._check_provider_status(),
            "models_discovered": len(self.available_models),
            "fallback_chain": self.fallback_chain,
            "buffered_logs": len(self.log_buffer),
            "last_flush": self.last_flush_time.isoformat()
        }
