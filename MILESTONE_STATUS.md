# Milestone Status

Last Updated: 2026-03-14

## Current Milestone: Milestone 1 - Foundation and Contracts

**Status: 100% Complete** ✅

### Milestone 1: Foundation and Contracts

**Deliverables:**
- ✅ Python project scaffold (directory structure)
- ✅ Configuration loading (settings.py with env overrides)
- ✅ Provider factory with OpenAI and Anthropic support
- ✅ Database bootstrap and migration setup
- ✅ Test harness with fixtures and mocks

**Acceptance Criteria:**
- ✅ App boots locally (main.py created and tested)
- ✅ Provider config can be loaded from file + env
- ✅ All 31 unit tests pass for provider and config contracts

**Completed Work:**
1. ✅ Created complete directory structure following revised plan
2. ✅ Created pyproject.toml with all dependencies
3. ✅ Created .env.example with all required variables
4. ✅ Implemented settings.py with pydantic-settings
5. ✅ Implemented provider abstraction layer:
   - base.py (BaseLLMProvider interface)
   - openai_provider.py (OpenAI implementation)
   - anthropic_provider.py (Anthropic implementation)
   - factory.py (ProviderFactory)
   - providers.py (config helpers)
6. ✅ Implemented database layer:
   - database.py (engine, session, init_db)
   - models.py (User, Conversation, Message models)
   - crud.py (CRUD operations for users)
7. ✅ Implemented authentication:
   - password.py (bcrypt hashing - migrated from passlib to bcrypt directly)
   - jwt.py (JWT token creation/verification)
8. ✅ Created test infrastructure:
   - conftest.py with fixtures
   - test_config.py (config tests - fixed settings singleton issue)
   - test_providers.py (provider tests - fixed error message matching)
   - test_auth.py (auth tests - all passing)
   - test_db.py (database tests - all passing)
9. ✅ Created FastAPI entry point:
   - main.py with lifespan handler, health check, and database initialization
10. ✅ Created .gitignore
11. ✅ Created README.md

**Fixes Applied:**
1. ✅ Migrated from passlib to bcrypt directly (resolved compatibility issue)
2. ✅ Fixed config tests to create fresh Settings instances
3. ✅ Fixed provider test error message matching
4. ✅ Created src/main.py FastAPI app with startup/shutdown hooks
5. ✅ Verified database initialization works correctly
6. ✅ All 31 unit tests passing

**Next Milestone: Milestone 2 - RAG MVP**

---

## Milestone 2: RAG MVP (Not Started)

**Status: 0% Complete** ⏳

**Deliverables:**
- Document loader for Markdown/Text
- Chunking strategy with metadata preservation
- FAISS index manager
- Retrieval tool with relevance threshold
- LangGraph flow: retrieve -> synthesize -> cite

---

## Milestone 3: Authenticated API MVP (Not Started)

**Status: 0% Complete** ⏳

---

## Milestone 4: Research Extensions (Not Started)

**Status: 0% Complete** ⏳

---

## Milestone 5: Advanced Operations (Not Started)

**Status: 0% Complete** ⏳

---

## Known Issues

1. ~~**bcrypt compatibility**~~ ✅ RESOLVED
   - Migrated from passlib to bcrypt directly for better compatibility

2. **tiktoken build failure** ⚠️ DEFERRED TO MILESTONE 2
   - Can't build from source without Rust
   - Not needed for Milestone 1, will address when implementing embeddings

3. ~~**Settings singleton in tests**~~ ✅ RESOLVED
   - Refactored tests to create fresh Settings instances

4. ~~**Missing entry point**~~ ✅ RESOLVED
   - Created src/main.py with FastAPI app initialization

---

## Dependencies Installed

- ✅ Core LangChain/LangGraph packages
- ✅ OpenAI and Anthropic provider packages
- ✅ FastAPI and Uvicorn
- ✅ SQLAlchemy and Alembic
- ✅ python-jose and PyJWT
- ✅ passlib and bcrypt
- ✅ pytest and testing tools
- ⏳ FAISS (deferred - will fail without Rust, but not needed for Milestone 1)
- ⏳ tiktoken (deferred - will fail without Rust, but not needed for Milestone 1)

---

## Environment Setup

- ✅ Virtual environment created (.venv)
- ✅ Dependencies installed via uv
- ✅ .env file created from template
- ⏳ .env populated with real API keys (user must do this)

---

## Quick Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run unit tests
PYTHONPATH=. pytest tests/unit/ -v -m unit

# Run specific test file
PYTHONPATH=. pytest tests/unit/test_config.py -v

# Check code
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```
