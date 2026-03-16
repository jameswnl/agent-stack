"""Unit tests for citation formatting."""

import pytest

from src.rag.citations import build_citations, format_citations
from src.rag.models import Chunk, RetrievalResult


@pytest.fixture
def sample_results():
    """Create sample retrieval results."""
    return [
        RetrievalResult(
            chunk=Chunk(
                content="RAG combines retrieval and generation.",
                metadata={"source": "doc1.md"},
                chunk_id="c1",
            ),
            score=0.9,
            rank=0,
        ),
        RetrievalResult(
            chunk=Chunk(
                content="FAISS is a vector index.",
                metadata={"source": "doc2.md"},
                chunk_id="c2",
            ),
            score=0.8,
            rank=1,
        ),
    ]


@pytest.mark.unit
def test_build_citations(sample_results):
    """Test building citations from retrieval results."""
    citations = build_citations(sample_results)
    assert len(citations) == 2
    assert citations[0].source == "doc1.md"
    assert citations[1].source == "doc2.md"
    assert citations[0].chunk_id == "c1"
    assert citations[0].excerpt is not None


@pytest.mark.unit
def test_build_citations_empty():
    """Test building citations from empty results."""
    assert build_citations([]) == []


@pytest.mark.unit
def test_build_citations_deduplicates_same_source_chunk():
    """Test that same source+chunk_id appears only once."""
    chunk = Chunk(
        content="Duplicate content",
        metadata={"source": "same.md"},
        chunk_id="x",
    )
    results = [
        RetrievalResult(chunk=chunk, score=0.9, rank=0),
        RetrievalResult(chunk=chunk, score=0.8, rank=1),
    ]
    citations = build_citations(results)
    assert len(citations) == 1


@pytest.mark.unit
def test_format_citations_numbered(sample_results):
    """Test formatting citations with numbers."""
    citations = build_citations(sample_results)
    out = format_citations(citations, numbered=True)
    assert "[1]" in out
    assert "[2]" in out
    assert "doc1.md" in out


@pytest.mark.unit
def test_format_citations_not_numbered(sample_results):
    """Test formatting citations without numbers."""
    citations = build_citations(sample_results)
    out = format_citations(citations, numbered=False)
    assert "doc1.md" in out
    assert "doc2.md" in out


@pytest.mark.unit
def test_format_citations_empty():
    """Test formatting empty citations."""
    assert format_citations([]) == ""
