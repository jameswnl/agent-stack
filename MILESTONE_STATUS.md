# Milestone Status

Last Updated: 2026-03-14

## Current Milestone: Milestone 1 - Foundation and Contracts

**Status: 90% Complete** ⏳

### Milestone 1: Foundation and Contracts

**Deliverables:**
- ✅ Python project scaffold (directory structure)
- ✅ Configuration loading (settings.py with env overrides)
- ✅ Provider factory with OpenAI and Anthropic support
- ✅ Database bootstrap and migration setup
- ⏳ Test harness with fixtures and mocks (needs test fixes)

**Acceptance Criteria:**
- ⏳ App boots locally (not yet tested - need to create main entry point)
- ✅ Provider config can be loaded from file + env
- ⏳ Unit tests pass for provider and config contracts (some failing due to env/bcrypt issues)

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
   - password.py (bcrypt hashing)
   - jwt.py (JWT token creation/verification)
8. ✅ Created test infrastructure:
   - conftest.py with fixtures
   - test_config.py (config tests)
   - test_providers.py (provider tests)
   - test_auth.py (auth tests)
   - test_db.py (database tests)
9. ✅ Created .gitignore
10. ✅ Created README.md

**Remaining Work:**
1. Fix test issues:
   - Config tests need to handle settings singleton properly
   - Provider tests need mock implementations for external calls
2. Create simple bootstrap script to verify app initialization
3. Test database initialization
4. Document how to run tests

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

1. **bcrypt compatibility**: Tests failing with bcrypt password length error
   - Need to upgrade bcrypt or handle test data differently

2. **tiktoken build failure**: Can't build from source without Rust
   - Using uv pip, so should use wheel if available
   - May need to specify newer tiktoken version or install Rust

3. **Settings singleton in tests**: Config tests don't properly isolate settings
   - Need to refactor tests to create fresh Settings instances or mock properly

4. **Missing entry point**: No main.py or app startup script yet
   - Need to create src/main.py for FastAPI app initialization

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
