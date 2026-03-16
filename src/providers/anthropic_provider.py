"""Anthropic provider implementation."""

from langchain_anthropic import ChatAnthropic
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings  # Anthropic doesn't have embeddings

from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider for chat.

    Note: Uses OpenAI for embeddings as Anthropic doesn't provide an embeddings API.
    This requires OPENAI_API_KEY to be set even when using Anthropic for chat.
    """

    DEFAULT_CHAT_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_EMBEDDINGS_MODEL = "text-embedding-3-small"

    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """Get Anthropic chat model.

        Args:
            **kwargs: Optional overrides (model, temperature, etc.)

        Returns:
            ChatAnthropic instance
        """
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("Anthropic API key is required")

        model_name = kwargs.get("model", self.DEFAULT_CHAT_MODEL)
        temperature = kwargs.get("temperature", 0.0)

        return ChatAnthropic(
            api_key=api_key,
            model=model_name,
            temperature=temperature,
            **{k: v for k, v in kwargs.items() if k not in ["model", "temperature"]},
        )

    def get_embeddings(self, **kwargs) -> Embeddings:
        """Get OpenAI embeddings (fallback for Anthropic).

        Args:
            **kwargs: Optional overrides (model, etc.)

        Returns:
            OpenAIEmbeddings instance
        """
        # Anthropic doesn't provide embeddings, use OpenAI
        openai_key = self.config.get("openai_api_key")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings when using Anthropic provider")

        model = kwargs.get("model", self.DEFAULT_EMBEDDINGS_MODEL)

        return OpenAIEmbeddings(api_key=openai_key, model=model, **{k: v for k, v in kwargs.items() if k != "model"})
