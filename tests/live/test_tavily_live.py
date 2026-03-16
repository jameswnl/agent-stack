"""Opt-in live tests for the Tavily web search adapter.

These tests call the real Tavily API and require:
  - TAVILY_API_KEY set in the environment
  - Network access

Run with: PYTHONPATH=. pytest tests/live/ -m live -v
"""

import os

import pytest

from src.tools.base import SearchResult
from src.tools.web_search import TavilySearchTool


pytestmark = pytest.mark.live

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
skip_reason = "TAVILY_API_KEY not set; skipping live Tavily tests"


@pytest.fixture
def tavily_tool():
    if not TAVILY_API_KEY:
        pytest.skip(skip_reason)
    return TavilySearchTool(api_key=TAVILY_API_KEY)


def test_live_search(tavily_tool):
    """Live Tavily search returns real web results."""
    results = tavily_tool.search("Python programming language", max_results=3)
    assert len(results) > 0
    assert all(isinstance(r, SearchResult) for r in results)
    assert all(r.url for r in results)
    assert all(r.content for r in results)
