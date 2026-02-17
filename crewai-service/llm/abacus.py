"""
Abacus.AI (qwen3-max via RouteLLM) LLM provider.
Uses OpenAI-compatible API at https://routellm.abacus.ai/v1.
"""

import logging

from openai import AsyncOpenAI
from config import settings
from llm.base import LLMResponse

logger = logging.getLogger(__name__)

# Cost per 1M tokens (qwen3-max via RouteLLM, Feb 2026 estimates)
INPUT_COST_PER_M = 2.00
OUTPUT_COST_PER_M = 6.00

# Fallback key (temporary until env vars are updated)
FALLBACK_KEY = "s2_1e30fa4a3d834bffb1b465d67eb1809e"


class AbacusProvider:
    name = "abacus"
    model = "qwen3-max"

    def __init__(self):
        api_key = settings.ABACUS_PRIMARY_KEY or settings.ABACUS_BACKUP_KEY or FALLBACK_KEY
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://routellm.abacus.ai/v1",
        )

    async def chat(
        self,
        messages: list[dict],
        system: str = "",
        temperature: float = 0.75,
    ) -> LLMResponse:
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})
        api_messages.extend(messages)

        # qwen3-max via RouteLLM
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=4096,
        )

        choice = response.choices[0]
        usage = response.usage

        # Safety: Ensure tokens are ints, even if SDK returns None
        input_tokens = 0
        output_tokens = 0

        if usage:
            input_tokens = getattr(usage, "prompt_tokens", 0) or 0
            output_tokens = getattr(usage, "completion_tokens", 0) or 0

        cost = (input_tokens / 1_000_000 * INPUT_COST_PER_M) + (output_tokens / 1_000_000 * OUTPUT_COST_PER_M)

        return LLMResponse(
            content=choice.message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            model=self.model,
        )
