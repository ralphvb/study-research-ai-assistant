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
        """Return complete final text and usage metrics ffrom Ollama."""
        max_tokens = self.settings.max_output_tokens

        payload = {
            "model": self.settings.model,
            "messages": [asdict(message) for message in messages],
            "stream": False,
            "options": {
                "num_ctx": self.settings.context_tokens,
                "num_predict": -1 if max_tokens is None else max_tokens,
            },
        }

        # Forward explicit thinking settings, including False.
        if self.settings.request_thinking is not None:
            payload["think"] = True

        base_url = str(self.settings.base_url).rstrip("/")
        request = Request(
            f"{base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        started_at = perf_counter()
        with urlopen(request, timeout=self.settings.timeout_seconds) as response:
            result = json.load(response)

        latency_seconds = perf_counter() - started_at

        message = result["message"]
        content = message["content"]
        
        if result.get("done") is not True or not isinstance(content, str):
            raise ValueError("Ollama returned an incomplete or invalid response.")

        content = content.strip()
        reason = result.get("done_reason")

        if reason == "length" or not content or "<think>" in content or "</think>" in content:
            raise ValueError(
                f"Ollama did not returned a final usable response. "
                f"Reason: {reason or 'n/d'}. "
                f"Final empty text: {'yes' if not content else 'no'}."
                f"Time: {latency_seconds:.2f} s."
                f"Generated Tokens: {result.get('eval_count', 'n/d')}. "
            )

        return ChatResponse(
            content=content,
            provider="Ollama",
            model=result["model"],
            latency_seconds=latency_seconds,
            input_tokens=result.get("prompt_eval_count"),
            output_tokens=result.get("eval_count"),
        )
