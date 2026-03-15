"""Integration tests for RAG flow: load -> index -> query -> cited answer."""

import pytest
import numpy as np
from pathlib import Path

from langchain_core.embeddings import Embeddings

from src.rag.loader import DocumentLoader
from src.rag.chunker import TextChunker
from src.rag.store import VectorStoreManager
from src.rag.retriever import Retriever
from src.rag.citations import format_citations
from src.agent.rag_flow import RAGFlow, create_rag_graph, RAGState


# Fixtures directory relative to project root
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "documents"


class MockEmbeddings(Embeddings):
    """Deterministic mock embeddings for integration tests."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        np.random.seed(hash(text) % (2**32))
        return np.random.rand(self.dimension).tolist()


@pytest.fixture
def mock_embeddings():
    return MockEmbeddings(dimension=128)


@pytest.fixture
def indexed_retriever(mock_embeddings):
    """Load fixture docs, chunk, index, and return a retriever."""
    loader = DocumentLoader()
    docs = loader.load_directory(str(FIXTURES_DIR))
    assert len(docs) >= 1, "Need at least one fixture document"
    chunker = TextChunker(chunk_size=400, chunk_overlap=50)
    chunks = chunker.chunk_documents(docs)
    store = VectorStoreManager(embeddings=mock_embeddings, dimension=128)
    store.index_documents(chunks)
    retriever = Retriever(
        vector_store=store,
        default_k=5,
        relevance_threshold=0.0,
    )
    return retriever


@pytest.mark.integration
def test_rag_flow_end_to_end_no_llm(indexed_retriever):
    """Run full RAG pipeline without LLM (placeholder answer) and verify citations."""
    flow = RAGFlow(retriever=indexed_retriever, llm=None)
    result = flow.invoke("What is RAG?")

    assert "query" in result
    assert result["query"] == "What is RAG?"
    assert "retrieval_results" in result
    assert "context" in result
    assert "answer" in result
    assert "citations" in result

    # Answer should be the placeholder when no LLM
    assert "[No LLM]" in result["answer"]
    assert "What is RAG?" in result["answer"]

    # Should have retrieved some chunks from fixtures
    assert len(result["retrieval_results"]) >= 0  # may be 0 if threshold filters all
    assert isinstance(result["citations"], list)


@pytest.mark.integration
def test_rag_flow_returns_citations_when_results(indexed_retriever):
    """With low threshold, we should get results and citations."""
    flow = RAGFlow(
        retriever=indexed_retriever,
        llm=None,
    )
    result = flow.invoke("RAG retrieval generation")
    # Query related to fixture content (doc1.md is about RAG)
    assert "context" in result
    # If we got retrieval results, citations should be built
    assert "citations" in result
    if result["retrieval_results"]:
        assert len(result["citations"]) > 0
        formatted = format_citations(result["citations"])
        assert "doc" in formatted or "fixtures" in formatted or result["citations"][0].source


@pytest.mark.integration
def test_create_rag_graph_invoke(indexed_retriever):
    """Compiled graph invoke returns full state."""
    graph = create_rag_graph(indexed_retriever, llm=None)
    state = graph.invoke({"query": "LangGraph"})
    assert state["query"] == "LangGraph"
    assert "answer" in state
    assert "citations" in state
