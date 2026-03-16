"""Abstract base for research tools."""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """A single result from a search tool."""

    title: str = Field(..., description="Result title or heading")
    url: str = Field(default="", description="Source URL")
    content: str = Field(..., description="Result content / snippet")
    score: float = Field(default=0.0, description="Relevance score (0-1)")
    source_type: str = Field(default="web", description="Source type identifier")


class BaseSearchTool(ABC):
    """Interface every search tool must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable tool name."""

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Execute search and return results.

        Args:
            query: Search query.
            max_results: Maximum results to return.

        Returns:
            List of SearchResult objects.
        """
