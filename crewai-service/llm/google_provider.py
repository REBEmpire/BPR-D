"""
Google (Gemini) LLM provider.
Uses the google-generativeai SDK.
"""

import logging
from typing import Any

import google.generativeai as genai

from api_healer import APIHealer
from config import settings
from llm.base import LLMResponse

logger = logging.getLogger(__name__)

# Cost per 1M tokens (gemini-3.0-pro, Feb 2026 estimates)
INPUT_COST_PER_M = 1.25
OUTPUT_COST_PER_M = 5.00


class GoogleProvider:
    name = "gemini"
    model = "gemini-3-pro-preview"

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.healer = APIHealer()

    async def chat(
        self,
        messages: list[dict],
        system: str = "",
        temperature: float = 0.9,
    ) -> LLMResponse:
        # Build Gemini content format from messages
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4096,
        )

        async def _call_gemini(model: str) -> Any:
            # Prepend system instruction if provided
            gemini_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=system if system else None,
            )
            return await gemini_model.generate_content_async(
                contents,
                generation_config=generation_config,
            )

        # Use healer to call API with retries and fallback
        response = await self.healer.heal_async(_call_gemini)

        content = response.text or ""

        # Extract token counts from usage metadata
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        cost = (input_tokens / 1_000_000 * INPUT_COST_PER_M) + (output_tokens / 1_000_000 * OUTPUT_COST_PER_M)

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            model=self.model,
        )
