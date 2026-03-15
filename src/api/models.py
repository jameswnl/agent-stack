"""API request and response models."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: str
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """User login payload."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Access token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user response."""

    id: int
    email: str
    full_name: Optional[str]
    is_active: bool


class IndexDocumentsRequest(BaseModel):
    """Document indexing request."""

    source_path: str
    recursive: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 200


class IndexDocumentsResponse(BaseModel):
    """Document indexing response."""

    document_count: int
    chunk_count: int
    vector_count: int


class ChatRequest(BaseModel):
    """Authenticated chat request."""

    query: str
    top_k: int = 5
    relevance_threshold: float = 0.5


class CitationResponse(BaseModel):
    """Citation returned by the chat endpoint."""

    source: str
    chunk_id: Optional[str]
    excerpt: Optional[str]


class ChatResponse(BaseModel):
    """Authenticated chat response."""

    answer: str
    citations: List[CitationResponse]
