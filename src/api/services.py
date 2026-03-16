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


def get_embedding_dimension(embeddings: Embeddings) -> int:
    """Return the configured embedding dimension with a safe default."""
    return int(getattr(embeddings, "dimension", 1536))


def resolve_allowed_source_path(source_path: str, allowed_base: Path) -> Path:
    """Resolve a source path and ensure it stays within the allowed base directory."""
    allowed_base = allowed_base.resolve()
    resolved = Path(source_path).resolve()
    try:
        resolved.relative_to(allowed_base)
    except ValueError as exc:
        raise ValueError("source_path outside allowed ingestion directory") from exc
    return resolved
