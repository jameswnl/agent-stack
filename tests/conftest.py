"""Pytest fixtures and configuration."""

import os
import tempfile
from typing import Generator

import numpy as np
import pytest
from langchain_core.embeddings import Embeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.db.models import User
from src.db.crud import create_user
from src.auth.jwt import create_access_token


class MockEmbeddings(Embeddings):
    """Deterministic mock embeddings for tests."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        np.random.seed(hash(text) % (2**32))
        return np.random.rand(self.dimension).tolist()


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def test_engine(test_db_path):
    """Create a test database engine."""
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = create_user(
        db=db_session,
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    return user


@pytest.fixture
def test_user_token(test_user):
    """Create a JWT token for the test user."""
    token = create_access_token(data={"sub": test_user.email})
    return token


@pytest.fixture
def test_user2(db_session):
    """Create a second test user for isolation tests."""
    user = create_user(
        db=db_session,
        email="test2@example.com",
        password="testpassword456",
        full_name="Test User 2"
    )
    return user


@pytest.fixture
def test_user2_token(test_user2):
    """Create a JWT token for the second test user."""
    token = create_access_token(data={"sub": test_user2.email})
    return token


@pytest.fixture
def mock_embeddings():
    """Create deterministic mock embeddings."""
    return MockEmbeddings(dimension=128)


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Getting Started

This is a sample document for testing RAG functionality.

## Installation

To install the system, run:

```bash
pip install example-package
```

## Configuration

Set the following environment variables:
- API_KEY: Your API key
- DATABASE_URL: Database connection string

## Troubleshooting

If you encounter errors, check the logs.
"""


@pytest.fixture
def sample_documents_dir(tmp_path, sample_markdown_content):
    """Create a temporary directory with sample documents."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create test markdown files
    (docs_dir / "getting_started.md").write_text(sample_markdown_content)
    (docs_dir / "api_reference.md").write_text("# API Reference\n\nAPI documentation here.")
    (docs_dir / "troubleshooting.md").write_text("# Troubleshooting\n\nCommon issues and solutions.")

    return docs_dir


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests with no external dependencies")
    config.addinivalue_line("markers", "integration: Integration tests with ephemeral services")
    config.addinivalue_line("markers", "contract: Contract tests for external adapters")
    config.addinivalue_line("markers", "live: Live tests requiring external services (opt-in)")
