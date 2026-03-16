"""LangGraph RAG workflow: retrieve -> synthesize -> cite."""

from typing import List, Optional, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.rag.citations import build_citations
from src.rag.models import Citation, RetrievalResult
from src.rag.retriever import Retriever

# Default prompt for synthesis when no custom prompt is provided
RAG_SYSTEM_PROMPT = """Answer the question using only the provided context. If the context does not contain relevant information, say so. Keep answers concise and cite sources by referring to the source labels in the context."""

RAG_USER_PROMPT_TEMPLATE = """Context:
{context}

Question: {query}

Answer (cite sources from the context):"""


class RAGState(TypedDict, total=False):
    """State for the RAG LangGraph workflow."""

    query: str
    retrieval_results: List[RetrievalResult]
    context: str
    answer: str
    citations: List[Citation]


def _retrieve_node(state: RAGState) -> dict:
    """Retrieve relevant chunks and build context."""
    query = state.get("query") or ""
    retriever: Retriever = state.get("_retriever")  # type: ignore
    if not retriever:
        return {"retrieval_results": [], "context": ""}
    results = retriever.retrieve(query)
    context = retriever.retrieve_with_context(query)
    return {"retrieval_results": results, "context": context}


def _synthesize_node(state: RAGState) -> dict:
    """Generate answer from context using LLM or placeholder."""
    query = state.get("query") or ""
    context = state.get("context") or ""
    llm: Optional[BaseChatModel] = state.get("_llm")  # type: ignore

    if llm:
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(context=context, query=query)
        messages = [
            SystemMessage(content=RAG_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
    else:
        # No LLM: placeholder for testing
        answer = f"[No LLM] Query: {query}. Context length: {len(context)} chars."
    return {"answer": answer}


def _cite_node(state: RAGState) -> dict:
    """Build citations from retrieval results."""
    results: List[RetrievalResult] = state.get("retrieval_results") or []
    citations = build_citations(results)
    return {"citations": citations}


def create_rag_graph(
    retriever: Retriever,
    llm: Optional[BaseChatModel] = None,
):
    """Build the RAG LangGraph workflow.

    Args:
        retriever: Retriever instance for vector search.
        llm: Optional chat model for synthesis; if None, a placeholder answer is used.

    Returns:
        Compiled LangGraph.
    """
    builder = StateGraph(RAGState)

    # Wrap nodes so they have access to retriever and llm via closure
    def retrieve_node(s: RAGState) -> dict:
        return _retrieve_node({**s, "_retriever": retriever})

    def synthesize_node(s: RAGState) -> dict:
        return _synthesize_node({**s, "_llm": llm})

    builder.add_node("retrieve", retrieve_node)
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("cite", _cite_node)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "synthesize")
    builder.add_edge("synthesize", "cite")
    builder.add_edge("cite", END)

    return builder.compile()


class RAGFlow:
    """High-level RAG flow: run retrieve -> synthesize -> cite."""

    def __init__(
        self,
        retriever: Retriever,
        llm: Optional[BaseChatModel] = None,
    ):
        self.retriever = retriever
        self.llm = llm
        self._graph = create_rag_graph(retriever, llm)

    def invoke(self, query: str) -> dict:
        """Run the RAG pipeline for a query.

        Args:
            query: User question.

        Returns:
            State dict with keys: query, retrieval_results, context, answer, citations.
        """
        result = self._graph.invoke({"query": query})
        return result
