"""
Anthropic (Claude) LLM provider.
Uses the official anthropic SDK.
"""

import logging

from anthropic import AsyncAnthropic

from config import settings
from llm.base import LLMResponse

logger = logging.getLogger(__name__)

# Cost per 1M tokens (claude-sonnet-4-5, Feb 2026)
INPUT_COST_PER_M = 3.00
OUTPUT_COST_PER_M = 15.00


class AnthropicProvider:
    name = "claude"
    model = "claude-sonnet-4-5-20250929"

    def __init__(self):
        self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def chat(
        self,
        messages: list[dict],
        system: str = "",
        temperature: float = 0.8,
    ) -> LLMResponse:
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system if system else "",
            messages=messages,
            temperature=temperature,
        )

        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1_000_000 * INPUT_COST_PER_M) + (output_tokens / 1_000_000 * OUTPUT_COST_PER_M)

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            model=self.model,
        )
