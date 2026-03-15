"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from .api.routes import auth, chat, documents, health
from .config.settings import settings
from .db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup: Initialize database
    init_db()
    app.state.user_data_dir = Path("data/users")
    app.state.user_data_dir.mkdir(parents=True, exist_ok=True)
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


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph RAG Service",
        "version": "0.1.0",
        "environment": settings.app_env
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development"
    )
