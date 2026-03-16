"""Research planner — classifies queries and selects tool strategy."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class QueryClass(str, Enum):
    """Classification of a user query."""

    RAG_ONLY = "rag_only"
    WEB_ONLY = "web_only"
    MIXED = "mixed"


class ResearchPlan(BaseModel):
    """Describes which tools to invoke for a query."""

    query: str = Field(..., description="Original user query")
    requested_class: QueryClass = Field(..., description="What the query signals")
    query_class: QueryClass = Field(..., description="Resolved class after tool availability")
    use_rag: bool = Field(default=True)
    use_web: bool = Field(default=False)
    search_queries: List[str] = Field(
        default_factory=list,
        description="Derived search queries for web search",
    )


# Keywords that strongly suggest web search is needed
_WEB_KEYWORDS = frozenset([
    "latest", "recent", "current", "today", "news", "update",
    "2025", "2026", "2027",
    "trending", "breaking",
    "compare with", "versus",
    "price", "stock", "weather",
    "who is", "what happened",
])

# Keywords that suggest internal docs are sufficient
_RAG_KEYWORDS = frozenset([
    "our", "internal", "codebase", "documentation", "config",
    "setting", "install", "setup", "troubleshoot",
    "how do i", "how to", "getting started",
])


def classify_query(
    query: str,
    has_rag_index: bool = True,
    has_web_search: bool = False,
) -> ResearchPlan:
    """Classify a query and produce a research plan.

    The classifier is intentionally simple (keyword-based) so it runs
    without an LLM call.  A future version can use the LLM itself to
    classify when available.

    Args:
        query: The user question.
        has_rag_index: Whether a RAG index exists for this user.
        has_web_search: Whether web search is available.

    Returns:
        A ResearchPlan describing which tools to use.
    """
    lower = query.lower()

    web_signal = any(kw in lower for kw in _WEB_KEYWORDS)
    rag_signal = any(kw in lower for kw in _RAG_KEYWORDS)

    # Determine requested query class from signals
    if web_signal and rag_signal:
        requested_class = QueryClass.MIXED
    elif web_signal:
        requested_class = QueryClass.WEB_ONLY
    else:
        requested_class = QueryClass.RAG_ONLY

    # Constrain to available tools
    use_rag = has_rag_index and requested_class in (QueryClass.RAG_ONLY, QueryClass.MIXED)
    use_web = has_web_search and requested_class in (QueryClass.WEB_ONLY, QueryClass.MIXED)

    # Fall back: if no tool is selected, prefer whatever is available
    if not use_rag and not use_web:
        if has_rag_index:
            use_rag = True
        elif has_web_search:
            use_web = True

    # Resolve the actual execution class based on what will run
    if use_rag and use_web:
        resolved_class = QueryClass.MIXED
    elif use_web:
        resolved_class = QueryClass.WEB_ONLY
    else:
        resolved_class = QueryClass.RAG_ONLY

    search_queries = [query] if use_web else []

    return ResearchPlan(
        query=query,
        requested_class=requested_class,
        query_class=resolved_class,
        use_rag=use_rag,
        use_web=use_web,
        search_queries=search_queries,
    )
