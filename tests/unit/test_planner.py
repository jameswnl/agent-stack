"""Unit tests for the research planner / query classifier."""

import pytest

from src.research.planner import QueryClass, classify_query


@pytest.mark.unit
def test_rag_only_query():
    """Internal doc queries should classify as RAG_ONLY."""
    plan = classify_query("How do I install the system?", has_rag_index=True, has_web_search=True)
    assert plan.requested_class == QueryClass.RAG_ONLY
    assert plan.query_class == QueryClass.RAG_ONLY
    assert plan.use_rag is True
    assert plan.use_web is False
    assert plan.search_queries == []


@pytest.mark.unit
def test_web_only_query():
    """Queries asking for current events classify as WEB_ONLY."""
    plan = classify_query("What is the latest news on AI?", has_rag_index=True, has_web_search=True)
    assert plan.requested_class == QueryClass.WEB_ONLY
    assert plan.query_class == QueryClass.WEB_ONLY
    assert plan.use_rag is False
    assert plan.use_web is True
    assert plan.search_queries == ["What is the latest news on AI?"]


@pytest.mark.unit
def test_mixed_query():
    """Queries with both internal and web signals classify as MIXED."""
    plan = classify_query(
        "What is the latest update to our documentation?",
        has_rag_index=True,
        has_web_search=True,
    )
    assert plan.requested_class == QueryClass.MIXED
    assert plan.query_class == QueryClass.MIXED
    assert plan.use_rag is True
    assert plan.use_web is True


@pytest.mark.unit
def test_fallback_when_no_web_search():
    """Web-classified queries fall back to RAG when web is unavailable."""
    plan = classify_query("What is the latest news?", has_rag_index=True, has_web_search=False)
    assert plan.requested_class == QueryClass.WEB_ONLY
    assert plan.query_class == QueryClass.RAG_ONLY  # resolved after fallback
    assert plan.use_rag is True  # fallback
    assert plan.use_web is False


@pytest.mark.unit
def test_fallback_when_no_rag_index():
    """RAG-classified queries fall back to web when no index exists."""
    plan = classify_query("How do I install?", has_rag_index=False, has_web_search=True)
    assert plan.requested_class == QueryClass.RAG_ONLY
    assert plan.query_class == QueryClass.WEB_ONLY  # resolved after fallback
    assert plan.use_rag is False
    assert plan.use_web is True  # fallback


@pytest.mark.unit
def test_neither_tool_available():
    """When nothing is available, both flags are False."""
    plan = classify_query("Tell me something", has_rag_index=False, has_web_search=False)
    assert plan.use_rag is False
    assert plan.use_web is False
    assert plan.query_class == QueryClass.RAG_ONLY  # default


@pytest.mark.unit
def test_case_insensitive_matching():
    """Keywords match regardless of casing."""
    plan = classify_query("LATEST NEWS PLEASE", has_rag_index=True, has_web_search=True)
    assert plan.requested_class == QueryClass.WEB_ONLY


@pytest.mark.unit
def test_plan_contains_original_query():
    """The returned plan includes the original query."""
    plan = classify_query("hello world", has_rag_index=True)
    assert plan.query == "hello world"


@pytest.mark.unit
def test_requested_vs_resolved_differ_on_fallback():
    """requested_class reflects query signals; query_class reflects actual execution."""
    plan = classify_query("What is the latest news?", has_rag_index=True, has_web_search=False)
    assert plan.requested_class == QueryClass.WEB_ONLY
    assert plan.query_class == QueryClass.RAG_ONLY
    assert plan.requested_class != plan.query_class
