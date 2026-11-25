"""Load and validate machine-specific settings for the Ollama client."""

from pathlib import Path

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class OllamaSettings(BaseSettings):
    """Read the settings for the Ollama server used by this checkout."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="SR_OLLAMA_",
        env_parse_none_str="null",
        env_ignore_empty=True,
        extra="ignore"
    )

    base_url: HttpUrl
    model: str = Field(min_length=1)
    context_tokens: int = Field(gt=0)
    timeout_seconds: float | None = Field(gt=0, allow_inf_nan=False)
    max_output_tokens: int | None = Field(default=None, gt=0)
    request_thinking: bool | None = True


class OpenAISettings(BaseSettings):
    """Load and validate the settings required for cloud interferance."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True
    )

    api_key: SecretStr = Field(
        min_length=1,
        validation_alias="OPENAI_API_KEY"
    )

    model: str = Field(
        min_length=1,
        validation_alias="SR_OPENAI_MODEL",
    )

    timeout_seconds: float = Field(
        gt=0,
        allow_inf_nan=False,
        validation_alias="SR_OPENAI_TIMEOUT_SECONDS"
    )
