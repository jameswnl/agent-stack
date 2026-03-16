"""Unit tests for mixed-source citation tracker."""

import pytest

from src.rag.models import Chunk, Citation, RetrievalResult
from src.research.citations import build_mixed_citations
from src.tools.base import SearchResult


def _make_rag_result(source: str, content: str, chunk_id: str = "c1") -> RetrievalResult:
    chunk = Chunk(
        content=content,
        metadata={"source": source},
        chunk_id=chunk_id,
    )
    return RetrievalResult(chunk=chunk, score=0.9, rank=1)


def _make_web_result(title: str, url: str, content: str) -> SearchResult:
    return SearchResult(title=title, url=url, content=content, score=0.8, source_type="web")


@pytest.mark.unit
def test_rag_only_citations():
    """Build citations from RAG results only."""
    rag = [_make_rag_result("doc.md", "RAG content")]
    citations = build_mixed_citations(rag_results=rag)

    assert len(citations) == 1
    assert citations[0].metadata["source_type"] == "rag"
    assert citations[0].source == "doc.md"


@pytest.mark.unit
def test_web_only_citations():
    """Build citations from web results only."""
    web = [_make_web_result("Page", "https://example.com", "Web content")]
    citations = build_mixed_citations(web_results=web)

    assert len(citations) == 1
    assert citations[0].metadata["source_type"] == "web"
    assert citations[0].source == "https://example.com"


@pytest.mark.unit
def test_mixed_citations():
    """Build citations from both RAG and web results."""
    rag = [_make_rag_result("doc.md", "RAG content")]
    web = [_make_web_result("Page", "https://example.com", "Web content")]

    citations = build_mixed_citations(rag_results=rag, web_results=web)

    assert len(citations) == 2
    types = {c.metadata["source_type"] for c in citations}
    assert types == {"rag", "web"}


@pytest.mark.unit
def test_deduplicates_rag_results():
    """Duplicate RAG sources are deduplicated."""
    rag = [
        _make_rag_result("doc.md", "Content A", chunk_id="c1"),
        _make_rag_result("doc.md", "Content B", chunk_id="c1"),
    ]
    citations = build_mixed_citations(rag_results=rag)
    assert len(citations) == 1


@pytest.mark.unit
def test_deduplicates_web_results():
    """Duplicate URLs are deduplicated."""
    web = [
        _make_web_result("Page 1", "https://example.com", "A"),
        _make_web_result("Page 1 again", "https://example.com", "B"),
    ]
    citations = build_mixed_citations(web_results=web)
    assert len(citations) == 1


@pytest.mark.unit
def test_empty_inputs():
    """No results produces no citations."""
    assert build_mixed_citations() == []
    assert build_mixed_citations(rag_results=[], web_results=[]) == []


@pytest.mark.unit
def test_excerpt_truncation():
    """Long content is truncated with ellipsis."""
    long_content = "x" * 300
    rag = [_make_rag_result("doc.md", long_content)]
    citations = build_mixed_citations(rag_results=rag)

    assert len(citations[0].excerpt) <= 203  # 200 + "..."
    assert citations[0].excerpt.endswith("...")


@pytest.mark.unit
def test_web_citation_preserves_title():
    """Web citations store the page title in metadata."""
    web = [_make_web_result("My Title", "https://example.com", "stuff")]
    citations = build_mixed_citations(web_results=web)

    assert citations[0].metadata["title"] == "My Title"
