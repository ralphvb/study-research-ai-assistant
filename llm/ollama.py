"""Adapt the Ollama HTTP API to the application's chat contract."""

import json
from collections.abc import Sequence
from dataclasses import asdict
from time import perf_counter
from urllib.request import Request, urlopen

from llm.contracts import ChatMessage, ChatResponse
from llm.settings import OllamaSettings


class OllamaClient:
    """Send chat request to the Ollama server configured for this machine."""

    def __init__(self, settings: OllamaSettings) -> None:
        """Initialize the client with validated server and model settings."""
        self.settings = settings

    def chat(self, messages: Sequence[ChatMessage]) -> ChatResponse:
        """Generate a reply from the messages supplied in conversation order."""

        payload = {
            "model": self.settings.model,
            "messages": [asdict(message) for message in messages],
            "stream": False,
            "think": True,
            "options": {"num_ctx": self.settings.context_tokens},
        }

        base_url = str(self.settings.base_url).rstrip("/")
        request = Request(
            f"{base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        started_at = perf_counter()

        with urlopen(request, timeout=self.settings.timeout_seconds) as response:
            result = json.load(response)

        latency_seconds = perf_counter() - started_at

        content = result["message"]["content"]

        if result.get("done") is not True or not isinstance(content, str):
            raise ValueError("Ollama returned an incomplete or invalid response.")

        content = content.strip()

        if not content or "<think>" in content or "</think>" in content:
            raise ValueError("Ollama did not return clean final text.")

        return ChatResponse(
            content=content,
            provider="Ollama",
            model=result["model"],
            latency_seconds=latency_seconds,
            input_tokens=result.get("prompt_eval_count"),
            output_tokens=result.get("eval_count"),
        )
