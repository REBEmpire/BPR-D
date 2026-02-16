"""
LLM provider abstraction for BPR&D meeting service.
Defines a common interface all providers implement.
"""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class LLMResponse:
    """Normalized response from any LLM provider."""
    content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol that all LLM providers must implement."""

    name: str
    model: str

    async def chat(
        self,
        messages: list[dict],
        system: str = "",
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send messages to the LLM and return a normalized response.

        Args:
            messages: List of {"role": "user"|"assistant", "content": str} dicts.
            system: System prompt (persona + instructions).
            temperature: Sampling temperature.

        Returns:
            LLMResponse with content and token usage.
        """
        ...
