"""Unit tests for provider abstraction."""

import pytest

from src.providers.anthropic_provider import AnthropicProvider
from src.providers.base import BaseLLMProvider
from src.providers.factory import ProviderFactory
from src.providers.openai_provider import OpenAIProvider


@pytest.mark.unit
def test_provider_factory_openai():
    """Test creating OpenAI provider."""
    config = {"api_key": "test-key"}
    provider = ProviderFactory.create_provider("openai", config)

    assert isinstance(provider, OpenAIProvider)
    assert isinstance(provider, BaseLLMProvider)
    assert provider.config["api_key"] == "test-key"


@pytest.mark.unit
def test_provider_factory_anthropic():
    """Test creating Anthropic provider."""
    config = {"api_key": "test-key", "openai_api_key": "test-openai-key"}
    provider = ProviderFactory.create_provider("anthropic", config)

    assert isinstance(provider, AnthropicProvider)
    assert isinstance(provider, BaseLLMProvider)
    assert provider.config["api_key"] == "test-key"


@pytest.mark.unit
def test_provider_factory_unsupported():
    """Test that unsupported provider raises ValueError."""
    config = {"api_key": "test-key"}

    with pytest.raises(ValueError, match="Unsupported provider"):
        ProviderFactory.create_provider("unsupported", config)


@pytest.mark.unit
def test_provider_factory_case_insensitive():
    """Test that provider names are case-insensitive."""
    config = {"api_key": "test-key"}

    provider1 = ProviderFactory.create_provider("OpenAI", config)
    provider2 = ProviderFactory.create_provider("OPENAI", config)

    assert isinstance(provider1, OpenAIProvider)
    assert isinstance(provider2, OpenAIProvider)


@pytest.mark.unit
def test_get_available_providers():
    """Test getting list of available providers."""
    providers = ProviderFactory.get_available_providers()

    assert "openai" in providers
    assert "anthropic" in providers
    assert isinstance(providers, list)
    assert "google" not in providers
    assert "ollama" not in providers


@pytest.mark.unit
def test_openai_provider_missing_key():
    """Test that OpenAI provider requires API key."""
    config = {}
    provider = OpenAIProvider(config)

    with pytest.raises(ValueError, match="OpenAI API key is required"):
        provider.get_chat_model()

    with pytest.raises(ValueError, match="OpenAI API key is required"):
        provider.get_embeddings()


@pytest.mark.unit
def test_anthropic_provider_missing_key():
    """Test that Anthropic provider requires API keys."""
    config = {"api_key": "test-anthropic-key"}
    provider = AnthropicProvider(config)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required for embeddings"):
        provider.get_embeddings()


@pytest.mark.contract
def test_openai_provider_chat_model_contract(monkeypatch):
    """Contract test: OpenAI provider returns valid chat model."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    config = {"api_key": "test-key"}
    provider = OpenAIProvider(config)

    # This will fail without real API key, but validates contract
    # In real tests, we'd mock the OpenAI client
    model = provider.get_chat_model()

    assert model is not None
    assert hasattr(model, "invoke")


@pytest.mark.contract
def test_openai_provider_embeddings_contract(monkeypatch):
    """Contract test: OpenAI provider returns valid embeddings."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    config = {"api_key": "test-key"}
    provider = OpenAIProvider(config)

    embeddings = provider.get_embeddings()

    assert embeddings is not None
    assert hasattr(embeddings, "embed_query")
