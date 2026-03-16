"""Mixed-source citation tracker for RAG + web results."""

from typing import List

from src.rag.models import Citation, RetrievalResult
from src.tools.base import SearchResult


def build_mixed_citations(
    rag_results: List[RetrievalResult] | None = None,
    web_results: List[SearchResult] | None = None,
) -> List[Citation]:
    """Build a unified citation list from RAG and/or web results.

    Citations are deduplicated by (source, chunk_id/url) and preserve
    their origin type in metadata so the caller can distinguish them.

    Args:
        rag_results: Chunks retrieved from the vector store.
        web_results: Results from a web search tool.

    Returns:
        Combined, deduplicated list of Citation objects.
    """
    rag_results = rag_results or []
    web_results = web_results or []

    citations: List[Citation] = []
    seen: set[tuple[str, str]] = set()

    # RAG citations
    for result in rag_results:
        chunk = result.chunk
        source = chunk.metadata.get("source", "unknown")
        chunk_id = chunk.chunk_id or ""
        key = (source, chunk_id)
        if key in seen:
            continue
        seen.add(key)

        excerpt = chunk.content[:200].strip()
        if len(chunk.content) > 200:
            excerpt += "..."

        citations.append(
            Citation(
                source=source,
                chunk_id=chunk_id or None,
                excerpt=excerpt,
                metadata={
                    "source_type": "rag",
                    "score": result.score,
                    "rank": result.rank,
                },
            )
        )

    # Web citations
    for result in web_results:
        key = (result.url or result.title, "web")
        if key in seen:
            continue
        seen.add(key)

        excerpt = result.content[:200].strip()
        if len(result.content) > 200:
            excerpt += "..."

        citations.append(
            Citation(
                source=result.url or result.title,
                chunk_id=None,
                excerpt=excerpt,
                metadata={
                    "source_type": "web",
                    "title": result.title,
                    "score": result.score,
                },
            )
        )

    return citations
