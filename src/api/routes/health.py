"""Health endpoints."""

from fastapi import APIRouter

from src.config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": settings.llm_provider,
    }

