"""
Conversation transcript manager for BPR&D meeting service.
Tracks the full meeting dialogue as it unfolds, providing each agent
with the complete conversation history so they can reference and respond
to each other's actual words.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Turn:
    """A single turn in the meeting conversation."""
    agent: str       # Who spoke
    phase: str       # Which meeting phase this was part of
    content: str     # What they said
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class Transcript:
    """Manages the full conversation transcript for a meeting.

    The key design decision: every agent call includes the full transcript
    as message history. This is what enables natural multi-turn dialogue.
    """

    def __init__(self):
        self.turns: list[Turn] = []

    def add_turn(self, agent: str, phase: str, content: str) -> None:
        """Record a new turn in the conversation."""
        self.turns.append(Turn(agent=agent, phase=phase, content=content))

    def to_messages(self, exclude_agent: str | None = None) -> list[dict]:
        """Convert transcript to LLM message format.

        Each agent's turns become 'assistant' messages (from the perspective
        of the current speaker) and all other agents' turns become 'user' messages.

        When exclude_agent is set, that agent's turns are 'assistant' and
        everyone else's are 'user'. This maintains proper role alternation
        for the LLM API.
        """
        messages = []
        for turn in self.turns:
            role = "assistant" if turn.agent == exclude_agent else "user"
            messages.append({
                "role": role,
                "content": f"[{turn.agent.upper()}]: {turn.content}",
            })

        # Ensure messages alternate roles properly — merge consecutive same-role messages
        merged = []
        for msg in messages:
            if merged and merged[-1]["role"] == msg["role"]:
                merged[-1]["content"] += "\n\n" + msg["content"]
            else:
                merged.append(msg)

        return merged

    def to_raw_messages(self) -> list[dict]:
        """Convert transcript to simple user messages for the synthesizer.

        All turns become user messages so the synthesizer can review the
        entire conversation without role alternation constraints.
        """
        if not self.turns:
            return []

        # Combine all turns into a single user message
        combined = "\n\n".join(
            f"[{turn.agent.upper()}]: {turn.content}"
            for turn in self.turns
        )
        return [{"role": "user", "content": combined}]

    def to_markdown(self) -> str:
        """Render the full transcript as readable markdown."""
        lines = []
        for turn in self.turns:
            lines.append(f"### {turn.agent.upper()}\n")
            lines.append(turn.content)
            lines.append("")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.turns)
