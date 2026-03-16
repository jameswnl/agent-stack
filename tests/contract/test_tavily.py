"""Contract tests for the Tavily web search adapter.

These tests validate that the TavilySearchTool correctly implements the
BaseSearchTool interface and normalises Tavily API responses.

The tests use a mocked Tavily client — they do NOT call the live API.
Use the ``live`` marker tests for real API verification.
"""

import pytest

from src.tools.base import BaseSearchTool, SearchResult
from src.tools.web_search import TavilySearchTool


class FakeTavilyClient:
    """Fake Tavily client that returns canned responses."""

    def __init__(self, **kwargs):
        pass

    def search(self, query: str, search_depth: str = "basic", max_results: int = 5):
        return {
            "results": [
                {
                    "title": f"Result for {query}",
                    "url": f"https://example.com/{query.replace(' ', '-')}",
                    "content": f"This is the content for {query}.",
                    "score": 0.92,
                },
            ]
        }


@pytest.fixture
def tavily_tool(monkeypatch):
    """TavilySearchTool with a mocked client."""
    monkeypatch.setattr("tavily.TavilyClient", FakeTavilyClient)
    return TavilySearchTool(api_key="contract-test-key")


@pytest.mark.contract
def test_implements_interface(tavily_tool):
    """Tavily tool is a BaseSearchTool."""
    assert isinstance(tavily_tool, BaseSearchTool)


@pytest.mark.contract
def test_has_name(tavily_tool):
    """Tool exposes a name."""
    assert isinstance(tavily_tool.name, str)
    assert len(tavily_tool.name) > 0


@pytest.mark.contract
def test_returns_search_results(tavily_tool):
    """Search returns a list of SearchResult objects."""
    results = tavily_tool.search("test")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, SearchResult) for r in results)


@pytest.mark.contract
def test_result_fields_populated(tavily_tool):
    """Each result has title, url, and content populated."""
    results = tavily_tool.search("contract test")
    r = results[0]
    assert r.title
    assert r.url
    assert r.content
    assert r.score > 0


@pytest.mark.contract
def test_source_type_is_web(tavily_tool):
    """Source type is always 'web' for Tavily results."""
    results = tavily_tool.search("hello")
    assert all(r.source_type == "web" for r in results)
