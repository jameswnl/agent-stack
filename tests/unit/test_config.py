"""Unit tests for configuration module."""

import pytest
from src.config.settings import Settings
from src.config.providers import get_provider_config


@pytest.mark.unit
def test_settings_defaults():
    """Test that settings have sensible defaults."""
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.database_url.startswith("sqlite")
    assert settings.llm_provider == "openai"
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_access_token_expire_minutes == 30
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000


@pytest.mark.unit
def test_settings_from_env(monkeypatch):
    """Test that settings can be overridden by environment variables."""
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    settings = Settings()

    assert settings.llm_provider == "anthropic"
    assert settings.api_port == 9000
    assert settings.openai_api_key == "test-key"


@pytest.mark.unit
def test_get_provider_config_openai(monkeypatch):
    """Test getting OpenAI provider configuration."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    config = get_provider_config("openai")

    assert "api_key" in config
    assert config["api_key"] == "test-openai-key"


@pytest.mark.unit
def test_get_provider_config_anthropic(monkeypatch):
    """Test getting Anthropic provider configuration."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    config = get_provider_config("anthropic")

    assert "api_key" in config
    assert config["api_key"] == "test-anthropic-key"
    assert "openai_api_key" in config  # Anthropic uses OpenAI for embeddings


@pytest.mark.unit
def test_get_provider_config_missing_key(monkeypatch):
    """Test that missing API key raises ValueError."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        get_provider_config("openai")
