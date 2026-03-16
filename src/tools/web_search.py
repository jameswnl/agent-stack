"""Tavily web search adapter."""

from typing import Any, List, Optional

from .base import BaseSearchTool, SearchResult


class TavilySearchTool(BaseSearchTool):
    """Web search tool backed by the Tavily API."""

    def __init__(
        self,
        api_key: str,
        search_depth: str = "basic",
        client: Optional[Any] = None,
    ):
        """Initialise with a Tavily API key or an injected client.

        Args:
            api_key: Tavily API key.
            search_depth: "basic" or "advanced".
            client: Optional pre-built client (useful for testing).
        """
        if not api_key:
            raise ValueError("TAVILY_API_KEY is required for web search")

        if client is not None:
            self._client = client
        else:
            try:
                from tavily import TavilyClient
            except ImportError as exc:
                raise ImportError(
                    "tavily-python is required for web search. "
                    "Install with: pip install tavily-python"
                ) from exc
            self._client = TavilyClient(api_key=api_key)

        self._search_depth = search_depth

    @property
    def name(self) -> str:
        return "tavily_web_search"

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search the web via Tavily.

        Args:
            query: Search query.
            max_results: Maximum results to return.

        Returns:
            List of SearchResult objects.
        """
        response = self._client.search(
            query=query,
            search_depth=self._search_depth,
            max_results=max_results,
        )

        results: List[SearchResult] = []
        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    source_type="web",
                )
            )
        return results
