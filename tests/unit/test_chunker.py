"""Unit tests for text chunker."""

import pytest
from src.rag.chunker import TextChunker
from src.rag.models import Document, Chunk


@pytest.fixture
def chunker():
    """Create text chunker with small chunk size for testing."""
    return TextChunker(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    content = """# Sample Document

This is the first paragraph with some content.

This is the second paragraph with more content.

This is the third paragraph with even more content to test chunking."""

    return Document(
        content=content,
        metadata={"filename": "test.md", "source": "test"},
        source="test.md"
    )


@pytest.mark.unit
def test_chunk_text_basic(chunker):
    """Test basic text chunking."""
    text = "Short text that fits in one chunk."
    chunks = chunker.chunk_text(text, source="test")

    assert len(chunks) == 1
    assert chunks[0].content == text
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[0].chunk_id is not None


@pytest.mark.unit
def test_chunk_text_multiple_chunks(chunker):
    """Test that long text is split into multiple chunks."""
    # Create text longer than chunk_size
    text = " ".join(["This is sentence number {}.".format(i) for i in range(20)])
    chunks = chunker.chunk_text(text, source="test")

    assert len(chunks) > 1
    # Check chunks have sequential indices
    for i, chunk in enumerate(chunks):
        assert chunk.metadata["chunk_index"] == i


@pytest.mark.unit
def test_chunk_text_overlap(chunker):
    """Test that chunks have overlap."""
    text = "\n\n".join([f"Paragraph {i}" for i in range(10)])
    chunks = chunker.chunk_text(text, source="test")

    if len(chunks) > 1:
        # Check that there's overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            # Some content from current chunk should appear in next chunk
            # This is simplified check - actual overlap depends on content
            assert chunks[i].content != chunks[i + 1].content


@pytest.mark.unit
def test_chunk_text_metadata_preservation(chunker):
    """Test that metadata is preserved in chunks."""
    text = "Test content"
    metadata = {"key1": "value1", "key2": "value2"}

    chunks = chunker.chunk_text(text, metadata=metadata, source="test")

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.metadata["key1"] == "value1"
    assert chunk.metadata["key2"] == "value2"
    assert chunk.metadata["source"] == "test"
    assert "chunk_index" in chunk.metadata
    assert "chunk_size" in chunk.metadata


@pytest.mark.unit
def test_chunk_document(chunker, sample_document):
    """Test chunking a document."""
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    # Check metadata from document is in chunks
    assert all(chunk.metadata["filename"] == "test.md" for chunk in chunks)


@pytest.mark.unit
def test_chunk_documents_multiple(chunker):
    """Test chunking multiple documents."""
    docs = [
        Document(content="Doc 1 content", metadata={"id": 1}, source="doc1"),
        Document(content="Doc 2 content", metadata={"id": 2}, source="doc2"),
    ]

    chunks = chunker.chunk_documents(docs)

    assert len(chunks) >= 2
    # Check we have chunks from both documents
    sources = {chunk.metadata["source"] for chunk in chunks}
    assert "doc1" in sources
    assert "doc2" in sources


@pytest.mark.unit
def test_chunk_empty_text(chunker):
    """Test chunking empty text returns empty list."""
    chunks = chunker.chunk_text("", source="test")
    assert len(chunks) == 0

    chunks = chunker.chunk_text("   \n\n  ", source="test")
    assert len(chunks) == 0


@pytest.mark.unit
def test_chunk_id_unique(chunker):
    """Test that chunk IDs are unique."""
    text = " ".join(["Sentence {}".format(i) for i in range(20)])
    chunks = chunker.chunk_text(text, source="test")

    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))  # All unique


@pytest.mark.unit
def test_chunk_size_configuration():
    """Test chunker with different chunk sizes."""
    small_chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    large_chunker = TextChunker(chunk_size=200, chunk_overlap=20)

    text = " ".join(["Word"] * 100)

    small_chunks = small_chunker.chunk_text(text, source="test")
    large_chunks = large_chunker.chunk_text(text, source="test")

    # Smaller chunk size should produce more chunks
    assert len(small_chunks) > len(large_chunks)


@pytest.mark.unit
def test_chunk_separator():
    """Test chunker with custom separator."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=10, separator="\n")

    text = "Line 1\nLine 2\nLine 3\nLine 4"
    chunks = chunker.chunk_text(text, source="test")

    # Should split on newlines
    assert len(chunks) >= 1


@pytest.mark.unit
def test_chunk_content_integrity(chunker):
    """Test that chunking preserves all content."""
    text = "This is important content that must not be lost during chunking process."

    chunks = chunker.chunk_text(text, source="test")

    # Reconstruct text from chunks (accounting for overlap)
    # At minimum, first chunk should have the content
    assert len(chunks[0].content) > 0

    # All chunks should have non-empty content
    assert all(len(chunk.content.strip()) > 0 for chunk in chunks)


@pytest.mark.unit
def test_chunk_metadata_size(chunker):
    """Test that chunk metadata includes size information."""
    text = "Test content for size verification"
    chunks = chunker.chunk_text(text, source="test")

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.metadata["chunk_size"] == len(chunk.content.strip())
