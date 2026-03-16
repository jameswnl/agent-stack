"""Integration tests for the research flow: plan -> retrieve/search -> synthesize -> cite."""

import pytest
from pathlib import Path

from src.rag.loader import DocumentLoader
from src.rag.chunker import TextChunker
from src.rag.store import VectorStoreManager
from src.rag.retriever import Retriever
from src.agent.research_flow import ResearchFlow
from src.tools.base import BaseSearchTool, SearchResult


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "documents"


class StubSearchTool(BaseSearchTool):
    """Deterministic stub for web search."""

    @property
    def name(self) -> str:
        return "stub_search"

    def search(self, query: str, max_results: int = 5):
        return [
            SearchResult(
                title="Stub Page",
                url="https://stub.example.com",
                content=f"Stub web answer for: {query}",
                score=0.85,
                source_type="web",
            )
        ]


@pytest.fixture
def indexed_retriever(mock_embeddings):
    """Load fixture docs, chunk, index, and return a retriever."""
    loader = DocumentLoader()
    docs = loader.load_directory(str(FIXTURES_DIR))
    chunker = TextChunker(chunk_size=200, chunk_overlap=40)
    chunks = chunker.chunk_documents(docs)
    store = VectorStoreManager(embeddings=mock_embeddings, dimension=128)
    store.index_documents(chunks)
    return Retriever(vector_store=store, default_k=3, relevance_threshold=0.0)


@pytest.mark.integration
def test_research_flow_rag_only(indexed_retriever):
    """Research flow with RAG only (no web search) returns answer + citations."""
    flow = ResearchFlow(retriever=indexed_retriever, search_tool=None, llm=None)
    result = flow.invoke("What is installation?")

    assert "[No LLM]" in result["answer"]
    assert len(result["citations"]) > 0
    assert all(c.metadata.get("source_type") == "rag" for c in result["citations"])
    assert result["plan"]["use_rag"] is True
    assert result["plan"]["use_web"] is False


@pytest.mark.integration
def test_research_flow_web_only():
    """Research flow with web search only returns web citations."""
    flow = ResearchFlow(retriever=None, search_tool=StubSearchTool(), llm=None)
    result = flow.invoke("What is the latest AI news?")

    assert "[No LLM]" in result["answer"]
    assert len(result["citations"]) > 0
    assert all(c.metadata.get("source_type") == "web" for c in result["citations"])
    assert result["plan"]["use_web"] is True


@pytest.mark.integration
def test_research_flow_mixed(indexed_retriever):
    """Research flow with both RAG and web search returns mixed citations."""
    flow = ResearchFlow(
        retriever=indexed_retriever,
        search_tool=StubSearchTool(),
        llm=None,
    )
    result = flow.invoke("What is the latest update to our documentation?")

    assert "[No LLM]" in result["answer"]
    types = {c.metadata.get("source_type") for c in result["citations"]}
    assert "rag" in types
    assert "web" in types
    assert result["plan"]["query_class"] == "mixed"


@pytest.mark.integration
def test_research_flow_graph_compiles():
    """The research graph compiles without errors even with no tools."""
    flow = ResearchFlow(retriever=None, search_tool=None, llm=None)
    result = flow.invoke("hello")
    assert "answer" in result
    assert "citations" in result
