"""FastAPI application entry point."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config.settings import settings
from .db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: cleanup if needed
    pass


# Create FastAPI app
app = FastAPI(
    title="LangGraph RAG Service",
    description="Multi-user RAG + Research service with authentication",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph RAG Service",
        "version": "0.1.0",
        "environment": settings.app_env
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": settings.llm_provider
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development"
    )
