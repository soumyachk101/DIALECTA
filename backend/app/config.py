"""Application configuration. Reads from env vars per TRD §8."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "production"] = "development"
    database_url: str = Field(
        default="postgresql+asyncpg://dialecta:dialecta@localhost:5432/dialecta"
    )
    token_encryption_key: str = Field(
        default="dev-only-replace-me-32bytes-min--"
    )

    # LLM providers
    anthropic_api_key: str = ""
    groq_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"
    groq_model: str = "llama-3.3-70b-versatile"

    # Streaming
    stream_first_token_timeout_s: float = 1.5
    agent_turn_token_budget: int = 80  # TRD §9: cap turns to ~60-80 tokens

    # Demo / fallback
    use_demo_fallback: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "chrome-extension://*"]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
