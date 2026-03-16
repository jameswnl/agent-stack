"""Document indexing endpoints."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.api.dependencies import get_current_user
from src.api.models import IndexDocumentsRequest, IndexDocumentsResponse
from src.api import services
from src.db.models import User
from src.rag.chunker import TextChunker
from src.rag.loader import DocumentLoader
from src.rag.store import VectorStoreManager

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/index", response_model=IndexDocumentsResponse)
def index_documents(
    request: IndexDocumentsRequest,
    fastapi_request: Request,
    current_user: User = Depends(get_current_user),
) -> IndexDocumentsResponse:
    """Index documents into a user-scoped vector store."""
    try:
        source_path = services.resolve_allowed_source_path(
            request.source_path,
            Path(fastapi_request.app.state.ingest_base_dir),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    loader = DocumentLoader()
    documents = loader.load_directory(
        str(source_path),
        recursive=request.recursive,
    )
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No supported documents found at source_path",
        )

    chunker = TextChunker(
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )
    chunks = chunker.chunk_documents(documents)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No chunks were produced from the provided documents",
        )

    embeddings = services.get_embeddings()
    store = VectorStoreManager(
        embeddings=embeddings,
        dimension=services.get_embedding_dimension(embeddings),
    )
    store.index_documents(chunks)

    base_dir = fastapi_request.app.state.user_data_dir
    store_path = services.get_user_store_path(Path(base_dir), current_user.id)
    store.save(str(store_path))

    return IndexDocumentsResponse(
        document_count=len(documents),
        chunk_count=len(chunks),
        vector_count=store.index.ntotal,
    )
