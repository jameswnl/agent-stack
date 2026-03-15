"""Citation formatting and tracking for RAG responses."""

from typing import List

from .models import Citation, RetrievalResult


def build_citations(results: List[RetrievalResult]) -> List[Citation]:
    """Build citation list from retrieval results.

    Args:
        results: Retrieved chunks with scores from vector search.

    Returns:
        List of Citation objects, one per unique source/chunk.
    """
    citations = []
    seen = set()

    for result in results:
        chunk = result.chunk
        source = chunk.metadata.get("source", "unknown")
        chunk_id = chunk.chunk_id or ""
        key = (source, chunk_id)
        if key in seen:
            continue
        seen.add(key)

        excerpt = chunk.content[:200].strip() + ("..." if len(chunk.content) > 200 else "")
        citation = Citation(
            source=source,
            chunk_id=chunk_id or None,
            excerpt=excerpt,
            metadata={"score": result.score, "rank": result.rank},
        )
        citations.append(citation)

    return citations


def format_citations(citations: List[Citation], numbered: bool = True) -> str:
    """Format citations as a readable reference block.

    Args:
        citations: List of Citation objects.
        numbered: If True, prefix with [1], [2], etc.

    Returns:
        Formatted string of citations.
    """
    if not citations:
        return ""

    lines = []
    for i, citation in enumerate(citations, 1):
        prefix = f"[{i}] " if numbered else ""
        lines.append(f"{prefix}{citation.format()}")
    return "\n".join(lines)
