"""Shared helpers for API routes."""

from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from src.config.providers import get_active_provider


def get_embeddings() -> Embeddings:
    """Return embeddings for the active provider."""
    provider = get_active_provider()
    return provider.get_embeddings()


def get_chat_model() -> BaseChatModel:
    """Return the active chat model."""
    provider = get_active_provider()
    return provider.get_chat_model()


def get_user_store_path(base_dir: Path, user_id: int) -> Path:
    """Return the persisted vector store path for a user."""
    return base_dir / str(user_id) / "faiss"

