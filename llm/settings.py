"""Load and validate machine-specific settings for the Ollama client."""

from pathlib import Path

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class OllamaSettings(BaseSettings):
    """Loads OLLAMA values from the environment and the project .env file."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="SR_OLLAMA_",
        extra="ignore"
    )

    base_url: HttpUrl
    model: str = Field(min_length=1)
    context_tokens: int = Field(gt=0)
    timeout_seconds: float = Field(gt=0, allow_inf_nan=False)
