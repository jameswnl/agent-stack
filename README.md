# LangGraph RAG + Research Service

Multi-user RAG service with research capabilities, built on LangGraph.

## Features

- **RAG over Internal Documents**: Query Markdown/Text documents with cited responses
- **Multi-User Authentication**: JWT-based auth with per-user data isolation
- **Configurable LLM Providers**: Switch between OpenAI, Anthropic, and others
- **Research Extensions** (Post-MVP): Web search, MCP integration, advanced workflows

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry (recommended) or pip

### Installation

```bash
# Clone repository
cd ~/ws/langgraph

# Install dependencies
poetry install

# Or with pip
pip install -e .

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
```

### Initialize Database

```bash
# Database will be auto-initialized on first run
# Or manually initialize:
python -c "from src.db.database import init_db; init_db()"
```

### Run Tests

```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# With coverage
pytest --cov=src --cov-report=html
```

### Development

```bash
# Format code
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
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
  fixtures/       # Test data and fixtures
```

## Milestones

- ✅ **Milestone 1**: Foundation and contracts
- 🚧 **Milestone 2**: RAG MVP
- ⏳ **Milestone 3**: Authenticated API MVP
- ⏳ **Milestone 4**: Research extensions
- ⏳ **Milestone 5**: Advanced operations

## License

MIT

## Contributing

See implementation plan in `IMPLEMENTATION_PLAN_REVISED.md`.
