"""Base provider interface for LLM and embeddings."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    Implementations must provide both chat models and embeddings
    to support RAG workflows.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with configuration.

        Args:
            config: Provider-specific configuration including API keys
        """
        self.config = config
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()

    @abstractmethod
    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """Get a chat model instance.

        Args:
            **kwargs: Optional overrides for model parameters

        Returns:
            Configured chat model instance
        """
        pass

    @abstractmethod
    def get_embeddings(self, **kwargs) -> Embeddings:
        """Get an embeddings model instance.

        Args:
            **kwargs: Optional overrides for embeddings parameters

        Returns:
            Configured embeddings instance
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_name})"
