# LangGraph RAG + Research Service

Multi-user RAG service with research capabilities, built on LangGraph.

## Features

- **RAG over Internal Documents**: Query Markdown/Text documents with cited responses
- **Multi-User Authentication**: JWT-based auth with per-user data isolation
- **Configurable LLM Providers**: Switch between OpenAI, Anthropic, and others
- **Research Extensions**: Web search (Tavily), query planning, mixed-source citations

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

### Installation

```bash
# Clone repository
git clone https://github.com/jameswnl/agent-stack.git
cd agent-stack

# Install dependencies (core + dev)
uv sync --extra dev

# Include optional research tools (Tavily, etc.)
uv sync --extra dev --extra research

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file with your configuration:

```env
# Required
OPENAI_API_KEY=your_key_here
LLM_PROVIDER=openai
DATABASE_URL=sqlite:///./data/chatbot.db

# Authentication
JWT_SECRET_KEY=your_secret_key_change_in_production

# Optional (for web search)
TAVILY_API_KEY=your_tavily_key
```

### Run Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest -m unit

# With coverage
uv run pytest --cov=src --cov-report=html

# Contract tests (mocked external services)
uv run pytest -m contract

# Live tests (requires real API keys, opt-in)
uv run pytest -m live
```

### Run the Server

```bash
uv run uvicorn src.main:app --reload
```

### Development

```bash
# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Add a dependency
uv add <package>

# Add a dev dependency
uv add --extra dev <package>
```

## Project Structure

```
src/
  agent/          # LangGraph workflow definitions
  api/            # FastAPI routes and server
  auth/           # JWT and password handling
  config/         # Settings and provider configuration
  db/             # Database models and CRUD
  providers/      # LLM provider abstractions
  rag/            # Document loading and retrieval
  research/       # Research planning and citations
  tools/          # Optional research tools

tests/
  unit/           # Unit tests (mocked dependencies)
  integration/    # Integration tests (ephemeral DB)
  contract/       # Contract tests for external adapters
  live/           # Opt-in live tests (require API keys)
  fixtures/       # Test data and fixtures
```

## Milestones

- ✅ **Milestone 1**: Foundation and contracts
- ✅ **Milestone 2**: RAG MVP
- ✅ **Milestone 3**: Authenticated API MVP
- ✅ **Milestone 4**: Research extensions
- ⏳ **Milestone 5**: Advanced operations

## License

MIT

## Contributing

See implementation plan in `IMPLEMENTATION_PLAN_REVISED.md`.
