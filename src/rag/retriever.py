"""Retrieval tool with relevance filtering."""

from typing import List, Optional
from langchain_core.embeddings import Embeddings

from .models import Chunk, RetrievalResult
from .store import VectorStoreManager


class Retriever:
    """High-level retrieval interface with relevance filtering."""

    def __init__(
        self,
        vector_store: VectorStoreManager,
        default_k: int = 5,
        relevance_threshold: float = 0.5
    ):
        """Initialize retriever.

        Args:
            vector_store: Vector store to search
            default_k: Default number of results to return
            relevance_threshold: Minimum relevance score (0-1) for results
        """
        self.vector_store = vector_store
        self.default_k = default_k
        self.relevance_threshold = relevance_threshold

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant chunks for a query.

        Args:
            query: Query text
            k: Number of results (uses default if None)
            threshold: Relevance threshold (uses default if None)

        Returns:
            List of relevant chunks sorted by relevance
        """
        k = k if k is not None else self.default_k

        # Search vector store
        # Note: vector_store.search uses L2 distance threshold, not score threshold
        # So we search with higher k and filter by score after
        results = self.vector_store.search(query, k=k * 2)

        # Filter by relevance score
        threshold = threshold if threshold is not None else self.relevance_threshold
        filtered_results = [
            result for result in results
            if result.score >= threshold
        ]

        # Limit to k results
        return filtered_results[:k]

    def retrieve_chunks(
        self,
        query: str,
        k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Chunk]:
        """Retrieve only the chunks (without scores).

        Args:
            query: Query text
            k: Number of results
            threshold: Relevance threshold

        Returns:
            List of relevant chunks
        """
        results = self.retrieve(query, k, threshold)
        return [result.chunk for result in results]

    def retrieve_with_context(
        self,
        query: str,
        k: Optional[int] = None,
        threshold: Optional[float] = None,
        separator: str = "\n\n"
    ) -> str:
        """Retrieve chunks and combine into context string.

        Args:
            query: Query text
            k: Number of results
            threshold: Relevance threshold
            separator: String to join chunks

        Returns:
            Combined context string
        """
        chunks = self.retrieve_chunks(query, k, threshold)

        if not chunks:
            return ""

        # Combine chunk contents
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            # Include source information
            source = chunk.metadata.get("source", "unknown")
            context_parts.append(f"[Source {i}: {source}]\n{chunk.content}")

        return separator.join(context_parts)

    def get_sources(
        self,
        query: str,
        k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[str]:
        """Get unique sources for retrieved chunks.

        Args:
            query: Query text
            k: Number of results
            threshold: Relevance threshold

        Returns:
            List of unique source identifiers
        """
        chunks = self.retrieve_chunks(query, k, threshold)
        sources = set()

        for chunk in chunks:
            source = chunk.metadata.get("source")
            if source:
                sources.add(source)

        return sorted(list(sources))
