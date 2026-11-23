"""Common types for languages model clients."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ChatResponse:
    content: str
    provider: str
    model: str
    latency_seconds: float
    input_tokens: int | None = None
    output_tokens: int | None = None


class ChatClient(Protocol):
    def chat(self, messages: Sequence[ChatMessage]) -> ChatResponse:
        """Generate a reply to the supplied messages."""
