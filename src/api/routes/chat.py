"""Authenticated chat endpoints."""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from langchain_core.language_models import BaseChatModel

from src.agent.rag_flow import RAGFlow
from src.api import services
from src.api.dependencies import get_current_user
from src.api.models import ChatRequest, ChatResponse, CitationResponse
from src.db.models import User
from src.rag.retriever import Retriever
from src.rag.store import VectorStoreManager

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
logger = logging.getLogger(__name__)


def _load_user_store(base_dir: Path, user_id: int) -> VectorStoreManager:
    embeddings = services.get_embeddings()
    store = VectorStoreManager(
        embeddings=embeddings,
        dimension=services.get_embedding_dimension(embeddings),
    )
    store_path = services.get_user_store_path(base_dir, user_id)
    store.load(str(store_path))
    return store


def _maybe_get_chat_model() -> BaseChatModel | None:
    try:
        return services.get_chat_model()
    except ValueError as exc:
        logger.info("Chat model unavailable, using placeholder response: %s", exc)
        return None


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    fastapi_request: Request,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """Run the user-scoped RAG flow for an authenticated request."""
    base_dir = Path(fastapi_request.app.state.user_data_dir)
    store_path = services.get_user_store_path(base_dir, current_user.id)
    if not store_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No indexed documents found for this user",
        )

    try:
        store = _load_user_store(base_dir, current_user.id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No indexed documents found for this user",
        ) from exc

    retriever = Retriever(
        vector_store=store,
        default_k=request.top_k,
        relevance_threshold=request.relevance_threshold,
    )
    flow = RAGFlow(retriever=retriever, llm=_maybe_get_chat_model())
    result = flow.invoke(request.query)

    citations = [
        CitationResponse(
            source=citation.source,
            chunk_id=citation.chunk_id,
            excerpt=citation.excerpt,
        )
        for citation in result.get("citations", [])
    ]
    return ChatResponse(answer=result["answer"], citations=citations)
