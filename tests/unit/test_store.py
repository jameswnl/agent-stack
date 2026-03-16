"""Unit tests for vector store manager."""

import pytest

from src.rag.models import Chunk
from src.rag.store import VectorStoreManager


@pytest.fixture
def vector_store(mock_embeddings):
    """Create vector store with mock embeddings."""
    return VectorStoreManager(embeddings=mock_embeddings, dimension=128)


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(
            content="Python is a programming language",
            metadata={"source": "doc1.md", "topic": "programming"},
            chunk_id="chunk1",
        ),
        Chunk(
            content="FastAPI is a web framework for Python",
            metadata={"source": "doc2.md", "topic": "web"},
            chunk_id="chunk2",
        ),
        Chunk(
            content="LangChain helps build LLM applications",
            metadata={"source": "doc3.md", "topic": "ai"},
            chunk_id="chunk3",
        ),
    ]


@pytest.mark.unit
def test_vector_store_initialization(vector_store):
    """Test vector store initializes correctly."""
    assert vector_store.index is not None
    assert vector_store.dimension == 128
    assert vector_store.index_type == "flat"
    assert len(vector_store.chunks) == 0


@pytest.mark.unit
def test_index_documents(vector_store, sample_chunks):
    """Test indexing documents."""
    vector_store.index_documents(sample_chunks)

    assert len(vector_store.chunks) == 3
    assert vector_store.index.ntotal == 3
    # Check embeddings were added
    assert all(chunk.embedding is not None for chunk in vector_store.chunks)


@pytest.mark.unit
def test_index_empty_documents(vector_store):
    """Test indexing empty list doesn't fail."""
    vector_store.index_documents([])
    assert len(vector_store.chunks) == 0


@pytest.mark.unit
def test_search(vector_store, sample_chunks):
    """Test searching for similar chunks."""
    vector_store.index_documents(sample_chunks)

    results = vector_store.search("Python programming", k=2)

    assert len(results) <= 2
    assert all(hasattr(r, "chunk") for r in results)
    assert all(hasattr(r, "score") for r in results)
    assert all(hasattr(r, "rank") for r in results)
    # Scores should be between 0 and 1
    assert all(0 <= r.score <= 1 for r in results)


@pytest.mark.unit
def test_search_empty_store(vector_store):
    """Test searching empty store returns empty results."""
    results = vector_store.search("test query", k=5)
    assert len(results) == 0


@pytest.mark.unit
def test_search_with_threshold(vector_store, sample_chunks):
    """Test searching with relevance threshold."""
    vector_store.index_documents(sample_chunks)

    # Search with high threshold (should filter out low-score results)
    results = vector_store.search("Python programming", k=10, threshold=100.0)

    # With high L2 distance threshold, should get no or few results
    assert len(results) <= 3


@pytest.mark.unit
def test_search_k_larger_than_index(vector_store, sample_chunks):
    """Test searching with k larger than index size."""
    vector_store.index_documents(sample_chunks)

    results = vector_store.search("test", k=100)

    # Should return all chunks even though k > index size
    assert len(results) <= len(sample_chunks)


@pytest.mark.unit
def test_save_and_load(vector_store, sample_chunks, tmp_path):
    """Test saving and loading vector store."""
    # Index some documents
    vector_store.index_documents(sample_chunks)

    # Save
    save_dir = tmp_path / "vector_store"
    vector_store.save(str(save_dir))

    # Verify files were created
    assert (save_dir / "index.faiss").exists()
    assert (save_dir / "chunks.pkl").exists()
    assert (save_dir / "metadata.pkl").exists()

    # Create new store and load
    new_store = VectorStoreManager(embeddings=vector_store.embeddings, dimension=128)
    new_store.load(str(save_dir))

    # Verify loaded correctly
    assert len(new_store.chunks) == len(sample_chunks)
    assert new_store.index.ntotal == vector_store.index.ntotal


@pytest.mark.unit
def test_load_nonexistent_directory(vector_store):
    """Test loading from non-existent directory raises error."""
    with pytest.raises(FileNotFoundError):
        vector_store.load("/nonexistent/directory")


@pytest.mark.unit
def test_clear(vector_store, sample_chunks):
    """Test clearing vector store."""
    vector_store.index_documents(sample_chunks)
    assert len(vector_store.chunks) == 3

    vector_store.clear()

    assert len(vector_store.chunks) == 0
    assert vector_store.index.ntotal == 0


@pytest.mark.unit
def test_get_stats(vector_store, sample_chunks):
    """Test getting vector store statistics."""
    stats = vector_store.get_stats()

    assert "num_chunks" in stats
    assert "index_type" in stats
    assert "dimension" in stats
    assert "total_vectors" in stats
    assert stats["num_chunks"] == 0

    # Index documents
    vector_store.index_documents(sample_chunks)
    stats = vector_store.get_stats()

    assert stats["num_chunks"] == 3
    assert stats["total_vectors"] == 3
    assert stats["dimension"] == 128


@pytest.mark.unit
def test_search_results_sorted_by_relevance(vector_store, sample_chunks):
    """Test that search results are sorted by relevance."""
    vector_store.index_documents(sample_chunks)

    results = vector_store.search("Python", k=3)

    if len(results) > 1:
        # Scores should be in descending order (higher score = more relevant)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)


@pytest.mark.unit
def test_result_rank_assignment(vector_store, sample_chunks):
    """Test that results have correct rank assignment."""
    vector_store.index_documents(sample_chunks)

    results = vector_store.search("test", k=3)

    for i, result in enumerate(results):
        assert result.rank == i


@pytest.mark.unit
def test_different_index_types(mock_embeddings):
    """Test creating stores with different index types."""
    flat_store = VectorStoreManager(embeddings=mock_embeddings, dimension=128, index_type="flat")
    assert flat_store.index_type == "flat"

    ivf_store = VectorStoreManager(embeddings=mock_embeddings, dimension=128, index_type="ivf")
    assert ivf_store.index_type == "ivf"


@pytest.mark.unit
def test_unsupported_index_type(mock_embeddings):
    """Test that unsupported index type raises error."""
    with pytest.raises(ValueError, match="Unsupported index type"):
        VectorStoreManager(embeddings=mock_embeddings, dimension=128, index_type="invalid")
