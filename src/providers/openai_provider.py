"""OpenAI provider implementation."""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider for chat and embeddings."""

    DEFAULT_CHAT_MODEL = "gpt-4o"
    DEFAULT_EMBEDDINGS_MODEL = "text-embedding-3-small"

    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """Get OpenAI chat model.

        Args:
            **kwargs: Optional overrides (model, temperature, etc.)

        Returns:
            ChatOpenAI instance
        """
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")

        model_name = kwargs.get("model", self.DEFAULT_CHAT_MODEL)
        temperature = kwargs.get("temperature", 0.0)

        return ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=temperature,
            **{k: v for k, v in kwargs.items() if k not in ["model", "temperature"]},
        )

    def get_embeddings(self, **kwargs) -> Embeddings:
        """Get OpenAI embeddings model.

        Args:
            **kwargs: Optional overrides (model, etc.)

        Returns:
            OpenAIEmbeddings instance
        """
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")

        model = kwargs.get("model", self.DEFAULT_EMBEDDINGS_MODEL)

        return OpenAIEmbeddings(api_key=api_key, model=model, **{k: v for k, v in kwargs.items() if k != "model"})
