"""Unit tests for the web search tool adapter."""

import pytest

from src.tools.base import BaseSearchTool, SearchResult
from src.tools.web_search import TavilySearchTool


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
        TavilySearchTool(api_key="")


@pytest.mark.unit
def test_tavily_implements_interface(monkeypatch):
    """TavilySearchTool is a BaseSearchTool."""
    # Patch TavilyClient so we don't need a real key
    import src.tools.web_search as ws_mod
    monkeypatch.setattr(
        ws_mod,
        "__import__",
        lambda *a, **kw: None,
        raising=False,
    )

    class FakeClient:
        def __init__(self, **kw):
            pass
        def search(self, **kw):
            return {"results": []}

    monkeypatch.setattr("tavily.TavilyClient", FakeClient, raising=False)

    tool = TavilySearchTool(api_key="test-key")
    assert isinstance(tool, BaseSearchTool)
    assert tool.name == "tavily_web_search"


@pytest.mark.unit
def test_tavily_normalises_results(monkeypatch):
    """TavilySearchTool normalises raw Tavily response into SearchResult objects."""

    class FakeClient:
        def __init__(self, **kw):
            pass
        def search(self, **kw):
            return {
                "results": [
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
                ]
            }

    monkeypatch.setattr("tavily.TavilyClient", FakeClient)

    tool = TavilySearchTool(api_key="test-key")
    results = tool.search("test query", max_results=2)

    assert len(results) == 2
    assert results[0].title == "Result 1"
    assert results[0].url == "https://example.com/1"
    assert results[0].source_type == "web"
    assert results[1].score == 0.7
