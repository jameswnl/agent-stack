# Quick Reference Guide

## Resume Development

```bash
# Navigate to project
cd ~/ws/langgraph

# Activate virtual environment
source .venv/bin/activate

# Check current status
cat CURRENT_SESSION_SUMMARY.md
cat MILESTONE_STATUS.md
cat TASKS.md
```

## Running Tests

```bash
# All unit tests
PYTHONPATH=. pytest tests/unit/ -v -m unit

# Specific test file
PYTHONPATH=. pytest tests/unit/test_config.py -v

# With coverage
PYTHONPATH=. pytest tests/unit/ -v -m unit --cov=src --cov-report=term-missing

# Integration tests (when available)
PYTHONPATH=. pytest tests/integration/ -v -m integration

# Contract tests (mocked external services)
PYTHONPATH=. pytest tests/ -v -m contract

# Live tests (requires real API keys, opt-in)
PYTHONPATH=. pytest tests/ -v -m live
```

## Code Quality

```bash
# Format code
.venv/bin/ruff format src/ tests/

# Lint code
.venv/bin/ruff check src/ tests/

# Type check
.venv/bin/mypy src/
```

## Dependencies

```bash
# Install new dependency
uv pip install <package>

# Update requirements.txt
uv pip freeze > requirements.txt

# Install from requirements
uv pip install -r requirements.txt
```

## Database

```bash
# Initialize database (creates tables)
PYTHONPATH=. python -c "from src.db.database import init_db; init_db()"

# Check database location
cat .env | grep DATABASE_URL

# SQLite database location (default)
ls -lh data/chatbot.db
```

## Environment Setup

```bash
# Check if .env exists
cat .env

# Set API keys (edit .env file)
# Required for Milestone 1 verification:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Project Structure

```bash
# View directory structure
tree -L 2 -I '__pycache__|.venv|.pytest_cache'

# Count lines of code
find src/ -name "*.py" | xargs wc -l
```

## Git

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: Milestone 1 foundation"

# Check status
git status
git log --oneline
```

## Development Workflow

### Starting a New Feature

1. Create a branch (if using git)
2. Write tests first (TDD: RED)
3. Implement minimal code to pass tests (TDD: GREEN)
4. Refactor while keeping tests green (TDD: REFACTOR)
5. Run linters and formatters
6. Commit

### Testing Changes

```bash
# Quick test during development
PYTHONPATH=. pytest tests/unit/test_<module>.py -v -k test_<specific_test>

# Full test suite before commit
PYTHONPATH=. pytest tests/unit/ -v -m unit --cov=src
```

## Debugging

```bash
# Run with debug output
PYTHONPATH=. pytest tests/unit/test_config.py -v -s

# Python debugger (add to code)
import pdb; pdb.set_trace()

# Check imports
PYTHONPATH=. python -c "from src.config.settings import settings; print(settings)"
```

## Current Blockers (Milestone 1)

1. **Test failures:** Config and bcrypt tests need fixes
2. **No app entry point:** Need to create `src/main.py`
3. **Deferred dependencies:** tiktoken and FAISS (need Rust, deferred to M2)

## Next Immediate Steps

1. Fix bcrypt compatibility in tests
2. Fix Settings singleton isolation in tests
3. Create `src/main.py` with FastAPI app initialization
4. Verify database initialization works
5. Test provider loading in running app
6. Run full test suite and verify Milestone 1 acceptance criteria

## Useful Commands Reference

```bash
# Find files
find src/ -name "*.py" -type f

# Search code
grep -r "TODO" src/

# Check Python version
python --version

# Check installed packages
uv pip list

# Disk usage
du -sh .venv/
```

## Documentation Files

- `README.md` - Project overview and setup
- `IMPLEMENTATION_PLAN_REVISED.md` - Full implementation plan with milestones
- `MILESTONE_STATUS.md` - Current milestone progress
- `TASKS.md` - Detailed task breakdown and status
- `CURRENT_SESSION_SUMMARY.md` - What was accomplished in last session
- `QUICKSTART.md` - This file (quick commands reference)

## Getting Help

If stuck, check:
1. `TASKS.md` for what's blocked and why
2. `MILESTONE_STATUS.md` for known issues
3. `CURRENT_SESSION_SUMMARY.md` for recent changes
4. Test output for specific errors
5. Implementation plan for design decisions
