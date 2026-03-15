"""Centralized configuration using pydantic-settings."""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_env: str = Field(default="development", description="Application environment")

    # Database
    database_url: str = Field(
        default="sqlite:///./data/chatbot.db",
        description="Database connection string"
    )

    # LLM Provider
    llm_provider: Literal["openai", "anthropic"] = Field(
        default="openai",
        description="Active LLM provider"
    )

    # Provider API Keys
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    google_api_key: str | None = Field(default=None, description="Google API key")

    # Authentication
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT secret key for token signing"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )

    # API Server
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")

    # LangSmith (Optional)
    langchain_tracing_v2: bool = Field(default=False, description="Enable LangSmith tracing")
    langchain_api_key: str | None = Field(default=None, description="LangSmith API key")
    langchain_project: str = Field(
        default="langgraph-rag-service",
        description="LangSmith project name"
    )

    # Research Tools (Optional - Milestone 4+)
    tavily_api_key: str | None = Field(default=None, description="Tavily API key")

    # Feature Flags
    enable_web_search: bool = Field(default=False, description="Enable web search tool")
    enable_mcp: bool = Field(default=False, description="Enable MCP integration")

    def validate_provider_key(self) -> None:
        """Validate that the selected provider has an API key configured."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        elif self.llm_provider == "anthropic" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for embeddings when LLM_PROVIDER=anthropic"
            )


# Global settings instance
settings = Settings()
