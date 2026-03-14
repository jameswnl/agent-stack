"""Provider configuration helpers."""

from typing import Dict, Any
from .settings import settings
from ..providers.factory import ProviderFactory
from ..providers.base import BaseLLMProvider


def get_provider_config(provider_name: str | None = None) -> Dict[str, Any]:
    """Get configuration for a provider.

    Args:
        provider_name: Provider name (defaults to settings.llm_provider)

    Returns:
        Provider configuration dictionary

    Raises:
        ValueError: If required API key is missing
    """
    provider_name = provider_name or settings.llm_provider

    config: Dict[str, Any] = {}

    if provider_name == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        config["api_key"] = settings.openai_api_key

    elif provider_name == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
        config["api_key"] = settings.anthropic_api_key
        # Anthropic uses OpenAI for embeddings
        config["openai_api_key"] = settings.openai_api_key

    elif provider_name == "google":
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for Google provider")
        config["api_key"] = settings.google_api_key

    else:
        raise ValueError(f"Unknown provider: {provider_name}")

    return config


def get_active_provider() -> BaseLLMProvider:
    """Get the active provider instance based on settings.

    Returns:
        Configured provider instance
    """
    provider_name = settings.llm_provider
    config = get_provider_config(provider_name)
    return ProviderFactory.create_provider(provider_name, config)
