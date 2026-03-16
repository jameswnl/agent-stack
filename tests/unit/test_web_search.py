"""Unit tests for the web search tool adapter."""

import pytest

from src.tools.base import BaseSearchTool, SearchResult
from src.tools.web_search import TavilySearchTool


class FakeClient:
    """Fake Tavily client for testing without the tavily package."""

    def __init__(self, results=None):
        self._results = results or []

    def search(self, **kw):
        return {"results": self._results}


@pytest.mark.unit
def test_search_result_model():
    """SearchResult accepts all fields."""
    r = SearchResult(
        title="Example",
        url="https://example.com",
        content="Some content",
        score=0.95,
        source_type="web",
    )
    assert r.title == "Example"
    assert r.source_type == "web"


@pytest.mark.unit
def test_search_result_defaults():
    """SearchResult has sensible defaults."""
    r = SearchResult(title="T", content="C")
    assert r.url == ""
    assert r.score == 0.0
    assert r.source_type == "web"


@pytest.mark.unit
def test_tavily_requires_api_key():
    """TavilySearchTool raises if no key is given."""
    with pytest.raises(ValueError, match="TAVILY_API_KEY is required"):
        TavilySearchTool(api_key="", client=FakeClient())


@pytest.mark.unit
def test_tavily_implements_interface():
    """TavilySearchTool is a BaseSearchTool."""
    tool = TavilySearchTool(api_key="test-key", client=FakeClient())
    assert isinstance(tool, BaseSearchTool)
    assert tool.name == "tavily_web_search"


@pytest.mark.unit
def test_tavily_normalises_results():
    """TavilySearchTool normalises raw Tavily response into SearchResult objects."""
    fake = FakeClient(results=[
        {
            "title": "Result 1",
            "url": "https://example.com/1",
            "content": "Content 1",
            "score": 0.9,
        },
        {
            "title": "Result 2",
            "url": "https://example.com/2",
            "content": "Content 2",
            "score": 0.7,
        },
    ])

    tool = TavilySearchTool(api_key="test-key", client=fake)
    results = tool.search("test query", max_results=2)

    assert len(results) == 2
    assert results[0].title == "Result 1"
    assert results[0].url == "https://example.com/1"
    assert results[0].source_type == "web"
    assert results[1].score == 0.7
