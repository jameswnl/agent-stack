"""Provider factory for creating LLM provider instances."""

from typing import Any, Dict

from .anthropic_provider import AnthropicProvider
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider


class ProviderFactory:
    """Factory for creating provider instances."""

    _PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str, config: Dict[str, Any]) -> BaseLLMProvider:
        """Create a provider instance.

        Args:
            provider_name: Name of the provider (openai, anthropic, etc.)
            config: Provider configuration including API keys

        Returns:
            Provider instance

        Raises:
            ValueError: If provider_name is not supported
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._PROVIDERS:
            available = ", ".join(cls._PROVIDERS.keys())
            raise ValueError(f"Unsupported provider: {provider_name}. Available providers: {available}")

        provider_class = cls._PROVIDERS[provider_name]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names.

        Returns:
            List of provider names
        """
        return list(cls._PROVIDERS.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseLLMProvider]) -> None:
        """Register a new provider class.

        Args:
            name: Provider name
            provider_class: Provider class implementing BaseLLMProvider
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise TypeError(f"{provider_class} must inherit from BaseLLMProvider")

        cls._PROVIDERS[name.lower()] = provider_class
