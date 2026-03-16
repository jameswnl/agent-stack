"""Unit tests for document loader."""

from pathlib import Path

import pytest

from src.rag.loader import DocumentLoader
from src.rag.models import Document


@pytest.fixture
def fixtures_dir():
    """Get path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "documents"


@pytest.fixture
def loader():
    """Create document loader instance."""
    return DocumentLoader()


@pytest.mark.unit
def test_load_file_markdown(loader, fixtures_dir):
    """Test loading a single Markdown file."""
    file_path = fixtures_dir / "doc1.md"
    doc = loader.load_file(str(file_path))

    assert isinstance(doc, Document)
    assert len(doc.content) > 0
    assert "RAG" in doc.content
    assert doc.metadata["filename"] == "doc1.md"
    assert doc.metadata["file_extension"] == ".md"
    assert "file_path" in doc.metadata
    assert "modified_time" in doc.metadata


@pytest.mark.unit
def test_load_file_text(loader, fixtures_dir):
    """Test loading a single Text file."""
    file_path = fixtures_dir / "doc3.txt"
    doc = loader.load_file(str(file_path))

    assert isinstance(doc, Document)
    assert "LangGraph" in doc.content
    assert doc.metadata["filename"] == "doc3.txt"
    assert doc.metadata["file_extension"] == ".txt"


@pytest.mark.unit
def test_load_file_not_found(loader):
    """Test loading non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        loader.load_file("/nonexistent/file.md")


@pytest.mark.unit
def test_load_file_unsupported_extension(loader, tmp_path):
    """Test loading file with unsupported extension raises error."""
    # Create temp file with unsupported extension
    test_file = tmp_path / "test.pdf"
    test_file.write_text("content")

    with pytest.raises(ValueError, match="Unsupported file extension"):
        loader.load_file(str(test_file))


@pytest.mark.unit
def test_load_directory(loader, fixtures_dir):
    """Test loading all documents from directory."""
    docs = loader.load_directory(str(fixtures_dir), recursive=False)

    assert len(docs) >= 3
    assert all(isinstance(doc, Document) for doc in docs)

    # Check we got markdown and text files
    extensions = {doc.metadata["file_extension"] for doc in docs}
    assert ".md" in extensions
    assert ".txt" in extensions


@pytest.mark.unit
def test_load_directory_not_found(loader):
    """Test loading from non-existent directory raises error."""
    with pytest.raises(FileNotFoundError):
        loader.load_directory("/nonexistent/directory")


@pytest.mark.unit
def test_load_directory_recursive(loader, tmp_path):
    """Test recursive directory loading."""
    # Create nested structure
    (tmp_path / "subdir").mkdir()
    (tmp_path / "doc1.md").write_text("# Doc 1")
    (tmp_path / "subdir" / "doc2.md").write_text("# Doc 2")

    # Load recursively
    docs = loader.load_directory(str(tmp_path), recursive=True)
    assert len(docs) == 2

    # Load non-recursively
    docs = loader.load_directory(str(tmp_path), recursive=False)
    assert len(docs) == 1


@pytest.mark.unit
def test_load_files(loader, fixtures_dir):
    """Test loading multiple specific files."""
    file_paths = [
        str(fixtures_dir / "doc1.md"),
        str(fixtures_dir / "doc2.md"),
    ]

    docs = loader.load_files(file_paths)

    assert len(docs) == 2
    assert all(isinstance(doc, Document) for doc in docs)


@pytest.mark.unit
def test_custom_extensions(fixtures_dir):
    """Test loader with custom file extensions."""
    loader = DocumentLoader(extensions={".md"})

    docs = loader.load_directory(str(fixtures_dir), recursive=False)

    # Should only load .md files, not .txt
    extensions = {doc.metadata["file_extension"] for doc in docs}
    assert ".md" in extensions
    assert ".txt" not in extensions


@pytest.mark.unit
def test_document_metadata_structure(loader, fixtures_dir):
    """Test that document metadata has expected structure."""
    file_path = fixtures_dir / "doc1.md"
    doc = loader.load_file(str(file_path))

    # Check required metadata fields
    assert "filename" in doc.metadata
    assert "file_path" in doc.metadata
    assert "file_size" in doc.metadata
    assert "file_extension" in doc.metadata
    assert "modified_time" in doc.metadata
    assert "created_time" in doc.metadata

    # Check types
    assert isinstance(doc.metadata["filename"], str)
    assert isinstance(doc.metadata["file_size"], int)
    assert doc.metadata["file_size"] > 0
