"""LangGraph research workflow: plan -> retrieve/search -> synthesize -> cite.

Extends the RAG-only flow to support optional web search with mixed-source
citations.  Falls back to the plain RAG path when web search is unavailable.
"""

import logging
from typing import List, Optional, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.rag.models import Citation, RetrievalResult
from src.rag.retriever import Retriever
from src.research.citations import build_mixed_citations
from src.research.planner import ResearchPlan, classify_query
from src.tools.base import BaseSearchTool, SearchResult

logger = logging.getLogger(__name__)

RESEARCH_SYSTEM_PROMPT = (
    "Answer the question using only the provided context. "
    "The context may contain both internal documents and web search results. "
    "Clearly distinguish between sources when citing. "
    "If the context does not contain relevant information, say so."
)

RESEARCH_USER_PROMPT = """Context:
{context}

Question: {query}

Answer (cite sources from the context):"""


class ResearchState(TypedDict, total=False):
    """State for the research LangGraph workflow."""

    query: str
    plan: dict  # serialised ResearchPlan
    retrieval_results: List[RetrievalResult]
    web_results: List[SearchResult]
    context: str
    answer: str
    citations: List[Citation]


# ── graph nodes ──────────────────────────────────────────────────────


def _build_plan_node(
    has_rag_index: bool,
    has_web_search: bool,
):
    """Return a plan node closure."""

    def plan_node(state: ResearchState) -> dict:
        query = state.get("query", "")
        plan = classify_query(query, has_rag_index=has_rag_index, has_web_search=has_web_search)
        return {"plan": plan.model_dump()}

    return plan_node


def _build_retrieve_node(retriever: Optional[Retriever]):
    """Return a retrieve node closure."""

    def retrieve_node(state: ResearchState) -> dict:
        plan = state.get("plan", {})
        if not plan.get("use_rag") or retriever is None:
            return {"retrieval_results": [], "context": ""}

        query = state.get("query", "")
        results = retriever.retrieve(query)

        # Build context from the already-fetched results to avoid a
        # second retrieval call that could diverge.
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result.chunk.metadata.get("source", "unknown")
            context_parts.append(f"[Source {i}: {source}]\n{result.chunk.content}")
        context = "\n\n".join(context_parts)

        return {"retrieval_results": results, "context": context}

    return retrieve_node


def _build_web_search_node(search_tool: Optional[BaseSearchTool]):
    """Return a web-search node closure."""

    def web_search_node(state: ResearchState) -> dict:
        plan = state.get("plan", {})
        if not plan.get("use_web") or search_tool is None:
            return {"web_results": []}

        queries = plan.get("search_queries", [state.get("query", "")])
        all_results: List[SearchResult] = []
        for q in queries:
            try:
                all_results.extend(search_tool.search(q, max_results=5))
            except Exception:
                logger.exception("Web search failed for query: %s", q)

        return {"web_results": all_results}

    return web_search_node


def _build_synthesize_node(llm: Optional[BaseChatModel]):
    """Return a synthesize node closure."""

    def synthesize_node(state: ResearchState) -> dict:
        query = state.get("query", "")

        # Merge RAG context and web context
        parts: list[str] = []
        rag_context = state.get("context", "")
        if rag_context:
            parts.append(rag_context)

        for i, wr in enumerate(state.get("web_results", []), 1):
            parts.append(f"[Web {i}: {wr.url or wr.title}]\n{wr.content}")

        full_context = "\n\n".join(parts) if parts else ""

        if llm and full_context:
            user_prompt = RESEARCH_USER_PROMPT.format(context=full_context, query=query)
            messages = [
                SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, "content") else str(response)
        else:
            answer = f"[No LLM] Query: {query}. Context length: {len(full_context)} chars."

        return {"answer": answer}

    return synthesize_node


def _cite_node(state: ResearchState) -> dict:
    """Build mixed citations from RAG + web results."""
    rag_results = state.get("retrieval_results", [])
    web_results = state.get("web_results", [])

    # Convert web_results dicts back to SearchResult objects if needed
    parsed_web: list[SearchResult] = []
    for wr in web_results:
        if isinstance(wr, dict):
            parsed_web.append(SearchResult(**wr))
        else:
            parsed_web.append(wr)

    citations = build_mixed_citations(rag_results=rag_results, web_results=parsed_web)
    return {"citations": citations}


# ── graph builder ────────────────────────────────────────────────────


def create_research_graph(
    retriever: Optional[Retriever] = None,
    search_tool: Optional[BaseSearchTool] = None,
    llm: Optional[BaseChatModel] = None,
):
    """Build the research LangGraph workflow.

    The graph always follows: plan -> retrieve + web_search -> synthesize -> cite.
    Nodes that are not applicable (e.g. no web search tool) simply pass through.

    Args:
        retriever: Optional RAG retriever.
        search_tool: Optional web search tool.
        llm: Optional chat model for synthesis.

    Returns:
        Compiled LangGraph.
    """
    plan_node_name = "plan_step"
    retrieve_node_name = "retrieve_step"
    web_search_node_name = "web_search_step"
    synthesize_node_name = "synthesize_step"
    cite_node_name = "cite_step"

    builder = StateGraph(ResearchState)

    builder.add_node(
        plan_node_name,
        _build_plan_node(
            has_rag_index=retriever is not None,
            has_web_search=search_tool is not None,
        ),
    )
    builder.add_node(retrieve_node_name, _build_retrieve_node(retriever))
    builder.add_node(web_search_node_name, _build_web_search_node(search_tool))
    builder.add_node(synthesize_node_name, _build_synthesize_node(llm))
    builder.add_node(cite_node_name, _cite_node)

    builder.add_edge(START, plan_node_name)
    builder.add_edge(plan_node_name, retrieve_node_name)
    builder.add_edge(plan_node_name, web_search_node_name)
    builder.add_edge(retrieve_node_name, synthesize_node_name)
    builder.add_edge(web_search_node_name, synthesize_node_name)
    builder.add_edge(synthesize_node_name, cite_node_name)
    builder.add_edge(cite_node_name, END)

    return builder.compile()


class ResearchFlow:
    """High-level wrapper for the research graph."""

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        search_tool: Optional[BaseSearchTool] = None,
        llm: Optional[BaseChatModel] = None,
    ):
        self.retriever = retriever
        self.search_tool = search_tool
        self.llm = llm
        self._graph = create_research_graph(retriever, search_tool, llm)

    def invoke(self, query: str) -> dict:
        """Run the research pipeline.

        Args:
            query: User question.

        Returns:
            State dict with answer and mixed citations.
        """
        return self._graph.invoke({"query": query})
