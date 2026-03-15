"""Data models for RAG system."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class Document(BaseModel):
    """Represents a loaded document."""

    model_config = ConfigDict(frozen=False)

    content: str = Field(..., description="Full text content of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata (filename, path, etc.)"
    )
    source: str = Field(..., description="Source identifier (file path or URL)")


class Chunk(BaseModel):
    """Represents a text chunk with metadata."""

    model_config = ConfigDict(frozen=False)

    content: str = Field(..., description="Chunk text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk metadata including source and position"
    )
    chunk_id: Optional[str] = Field(None, description="Unique chunk identifier")
    embedding: Optional[list[float]] = Field(None, description="Vector embedding")


class RetrievalResult(BaseModel):
    """Represents a retrieval result with relevance score."""

    chunk: Chunk = Field(..., description="Retrieved chunk")
    score: float = Field(..., description="Relevance score (0-1)")
    rank: int = Field(..., description="Result ranking position")


class Citation(BaseModel):
    """Represents a source citation."""

    source: str = Field(..., description="Source identifier")
    chunk_id: Optional[str] = Field(None, description="Referenced chunk ID")
    excerpt: Optional[str] = Field(None, description="Relevant text excerpt")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional citation metadata"
    )

    def format(self) -> str:
        """Format citation as string.

        Returns:
            Formatted citation string
        """
        if self.excerpt:
            return f"[{self.source}]: {self.excerpt[:100]}..."
        return f"[{self.source}]"
