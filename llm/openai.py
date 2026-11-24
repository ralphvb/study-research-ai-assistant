"""Adapt the OpenAI Responses AI to the application's chat contract."""

from collections.abc import Sequence
from time import perf_counter

from openai import OpenAI

from llm.contracts import ChatMessage, ChatResponse
from llm.settings import OpenAISettings


class OpenAICLient:
    """Send chat messages to the configured OpenAI model."""

    def __init__(self, settings: OpenAISettings) -> None:
        """Initialize the SDK with a project key and a request timeout."""
        self.model = settings.model
        self.client = OpenAI(
            api_key=settings.api_key.get_secret_value(),
            timeout=settings.timeout_seconds,
            max_retries=0,
        )

    def chat(self, messages: Sequence[ChatMessage]) -> ChatResponse:
        """Generate a reply from messages supplied in conversation order."""
        input_message = [
            {"role": message.role, "content": message.content} for message in messages
        ]

        start_at = perf_counter()

        response = self.client.responses.create(
            model=self.model, input=input_message, max_output_tokens=256, store=False
        )

        latency_seconds = perf_counter() - start_at

        if response.status != "completed":
            raise ValueError(f"OpenAI resposne did not complete: {response.status}")

        content = response.output_text.strip()

        if not content:
            raise ValueError(f"OpenAI response did not complete: {response.status}")

        usage = response.usage

        return ChatResponse(
            content=content,
            provider="OpenAI",
            model=response.model,
            latency_seconds=latency_seconds,
            input_tokens=usage.input_tokens if usage else None,
            output_tokens=usage.output_tokens if usage else None,
        )
