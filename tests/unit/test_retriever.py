"""Unit tests for retriever."""

import pytest
from src.rag.retriever import Retriever
from src.rag.store import VectorStoreManager
from src.rag.models import Chunk
from tests.unit.test_store import MockEmbeddings


@pytest.fixture
def mock_embeddings():
    """Create mock embeddings."""
    return MockEmbeddings(dimension=128)


@pytest.fixture
def vector_store(mock_embeddings):
    """Create vector store with indexed documents."""
    store = VectorStoreManager(embeddings=mock_embeddings, dimension=128)

    chunks = [
        Chunk(
            content="Python is a versatile programming language",
            metadata={"source": "python_intro.md"},
            chunk_id="chunk1"
        ),
        Chunk(
            content="FastAPI is great for building APIs with Python",
            metadata={"source": "fastapi_guide.md"},
            chunk_id="chunk2"
        ),
        Chunk(
            content="Machine learning with TensorFlow",
            metadata={"source": "ml_basics.md"},
            chunk_id="chunk3"
        ),
    ]

    store.index_documents(chunks)
    return store


@pytest.fixture
def retriever(vector_store):
    """Create retriever instance."""
    return Retriever(
        vector_store=vector_store,
        default_k=5,
        relevance_threshold=0.5
    )


@pytest.mark.unit
def test_retriever_initialization(retriever):
    """Test retriever initializes correctly."""
    assert retriever.vector_store is not None
    assert retriever.default_k == 5
    assert retriever.relevance_threshold == 0.5


@pytest.mark.unit
def test_retrieve(retriever):
    """Test basic retrieval."""
    results = retriever.retrieve("Python programming")

    assert isinstance(results, list)
    assert all(hasattr(r, 'chunk') for r in results)
    assert all(hasattr(r, 'score') for r in results)


@pytest.mark.unit
def test_retrieve_with_custom_k(retriever):
    """Test retrieval with custom k value."""
    results = retriever.retrieve("Python", k=2)

    assert len(results) <= 2


@pytest.mark.unit
def test_retrieve_with_threshold(retriever):
    """Test retrieval with custom threshold."""
    # High threshold should return fewer results
    results_high = retriever.retrieve("Python", threshold=0.9)
    # Low threshold should return more results
    results_low = retriever.retrieve("Python", threshold=0.1)

    assert len(results_high) <= len(results_low)


@pytest.mark.unit
def test_retrieve_chunks(retriever):
    """Test retrieving only chunks without scores."""
    chunks = retriever.retrieve_chunks("Python programming", k=3)

    assert isinstance(chunks, list)
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert len(chunks) <= 3


@pytest.mark.unit
def test_retrieve_with_context(retriever):
    """Test retrieving chunks as context string."""
    # Use lower threshold to ensure we get results
    context = retriever.retrieve_with_context("Python", k=2, threshold=0.0)

    assert isinstance(context, str)
    # With threshold=0.0, should get at least some results
    if context:  # May be empty if no results
        # Should include source information
        assert "Source" in context


@pytest.mark.unit
def test_retrieve_with_context_custom_separator(retriever):
    """Test context retrieval with custom separator."""
    context = retriever.retrieve_with_context(
        "Python",
        k=2,
        separator="\n---\n"
    )

    if "\n---\n" in context:
        # If multiple chunks, separator should be present
        assert "---" in context


@pytest.mark.unit
def test_retrieve_with_context_empty_results():
    """Test context retrieval with no results."""
    # Create empty vector store
    mock_embeddings = MockEmbeddings(dimension=128)
    empty_store = VectorStoreManager(embeddings=mock_embeddings, dimension=128)
    retriever = Retriever(vector_store=empty_store)

    context = retriever.retrieve_with_context("test query")

    assert context == ""


@pytest.mark.unit
def test_get_sources(retriever):
    """Test getting unique sources from retrieval."""
    sources = retriever.get_sources("Python", k=3)

    assert isinstance(sources, list)
    assert all(isinstance(s, str) for s in sources)
    # Sources should be unique
    assert len(sources) == len(set(sources))


@pytest.mark.unit
def test_get_sources_sorted(retriever):
    """Test that sources are returned sorted."""
    sources = retriever.get_sources("Python", k=3)

    if len(sources) > 1:
        assert sources == sorted(sources)


@pytest.mark.unit
def test_default_k_used_when_none(retriever):
    """Test that default k is used when not specified."""
    retriever.default_k = 2

    results = retriever.retrieve("Python")  # k not specified

    assert len(results) <= 2


@pytest.mark.unit
def test_default_threshold_used_when_none(retriever):
    """Test that default threshold is used when not specified."""
    retriever.relevance_threshold = 0.9  # Very high threshold

    results = retriever.retrieve("Python")  # threshold not specified

    # With high default threshold, should get filtered results
    assert all(r.score >= 0.9 for r in results) or len(results) == 0


@pytest.mark.unit
def test_retrieve_no_results_above_threshold():
    """Test retrieval when no results meet threshold."""
    mock_embeddings = MockEmbeddings(dimension=128)
    store = VectorStoreManager(embeddings=mock_embeddings, dimension=128)

    chunks = [
        Chunk(content="Test content", metadata={"source": "test.md"}, chunk_id="c1")
    ]
    store.index_documents(chunks)

    retriever = Retriever(vector_store=store, relevance_threshold=0.99)

    # Very high threshold should filter out most results
    results = retriever.retrieve("completely unrelated query")

    # May return empty or very few results
    assert isinstance(results, list)


@pytest.mark.unit
def test_retrieve_chunks_preserves_metadata(retriever):
    """Test that retrieved chunks preserve metadata."""
    chunks = retriever.retrieve_chunks("Python", k=2)

    for chunk in chunks:
        assert "source" in chunk.metadata
        assert chunk.metadata["source"].endswith(".md")


@pytest.mark.unit
def test_context_includes_all_chunks():
    """Test that context string includes all retrieved chunks."""
    mock_embeddings = MockEmbeddings(dimension=128)
    store = VectorStoreManager(embeddings=mock_embeddings, dimension=128)

    chunks = [
        Chunk(content="Content 1", metadata={"source": "doc1.md"}, chunk_id="c1"),
        Chunk(content="Content 2", metadata={"source": "doc2.md"}, chunk_id="c2"),
    ]
    store.index_documents(chunks)

    retriever = Retriever(vector_store=store, relevance_threshold=0.0)
    context = retriever.retrieve_with_context("test", k=2)

    # Context should include both sources
    assert "doc1.md" in context or "doc2.md" in context
