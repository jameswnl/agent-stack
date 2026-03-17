# Quick Reference Guide

## Resume Development

```bash
cd ~/ws/langgraph
cat MILESTONE_STATUS.md
cat TASKS.md
```

## Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest -m unit -v

# Specific test file
uv run pytest tests/unit/test_config.py -v

# With coverage
uv run pytest -m unit --cov=src --cov-report=term-missing

# Integration tests
uv run pytest -m integration -v

# Contract tests (mocked external services)
uv run pytest -m contract -v

# Live tests (requires real API keys, opt-in)
uv run pytest -m live -v
```

## Code Quality

```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## Dependencies

```bash
# Install core + dev deps
uv sync --extra dev

# Include optional research tools
uv sync --extra dev --extra research

# Add a new dependency
uv add <package>

# Add a dev dependency
uv add --extra dev <package>
```

## Database

```bash
# Initialize database (creates tables)
uv run python -c "from src.db.database import init_db; init_db()"

# Check database location
cat .env | grep DATABASE_URL
```

## Environment Setup

```bash
# Copy template
cp .env.example .env

# Required keys
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">

# Optional
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

## Run the Server

```bash
uv run uvicorn src.main:app --reload
```

## Documentation Files

- `README.md` - Project overview and setup
- `IMPLEMENTATION_PLAN_REVISED.md` - Full implementation plan with milestones
- `MILESTONE_STATUS.md` - Current milestone progress
- `TASKS.md` - Detailed task breakdown and status
- `QUICKSTART.md` - This file (quick commands reference)
