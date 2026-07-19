"""
Configuration module for the Fan Journey Concierge application.

Defines the Settings class using pydantic-settings to load configuration
from environment variables or a .env file.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from dotenv import load_dotenv

# Explicitly load .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.

    Uses pydantic-settings so that every field can be overridden by a
    matching environment variable at deploy time without code changes.
    The class provides a computed `genai_mode` property so the rest of the
    application only ever asks "am I live or mock?" — they never inspect
    the raw API key, keeping the key out of all non-config modules.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # API key for Anthropic Claude (can be None/empty for mock mode)
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Claude model identifier (default: claude-sonnet-4-6)
    anthropic_model: str = Field(default="claude-sonnet-4-6", alias="ANTHROPIC_MODEL")

    # Comma-separated list of allowed CORS origins
    allowed_origins: str = Field(default="", alias="ALLOWED_ORIGINS")

    # Rate limiting configuration (requests per minute per client IP)
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    @computed_field
    @property
    def genai_mode(self) -> str:
        """
        Determines the GenAI mode of the application.

        Returns "live" if ANTHROPIC_API_KEY is configured, else "mock".
        This fallback guarantees that the application runs and demos successfully
        even in offline settings or without a configured API key.
        """
        if self.anthropic_api_key and self.anthropic_api_key.strip():
            return "live"
        return "mock"

    @property
    def allowed_origins_list(self) -> List[str]:
        """
        Parses the ALLOWED_ORIGINS comma-separated string into a list of origins.
        """
        if not self.allowed_origins.strip():
            return []
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


# Singleton instance of settings to be imported and used across modules.
settings = Settings()
