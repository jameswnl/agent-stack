# Milestone Status

Last Updated: 2026-03-15

## Current Milestone: Milestone 2 - RAG MVP

**Status: 60% Complete** ⏳

---

## Milestone 1: Foundation and Contracts

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

## Milestone 2: RAG MVP (In Progress)

**Status: 60% Complete** ⏳

**Deliverables:**
- ✅ Document loader for Markdown/Text (Phase 1)
- ✅ Chunking strategy with metadata preservation (Phase 1)
- ✅ FAISS index manager (Phase 2)
- ✅ Retrieval tool with relevance threshold (Phase 2)
- ⏳ Citation tracking (Phase 3 - remaining)
- ⏳ LangGraph flow: retrieve -> synthesize -> cite (Phase 3 - remaining)

**Acceptance Criteria:**
- ✅ Documents can be indexed from a directory
- ⏳ RAG query returns cited answer from indexed fixtures
- ⏳ No external network dependency required for core tests

**Completed Work (Phases 1 & 2):**

### Phase 1: Document Processing ✅
1. ✅ Created `src/rag/models.py` - Data models (Document, Chunk, RetrievalResult, Citation)
2. ✅ Implemented `src/rag/loader.py` - DocumentLoader for Markdown/Text files
   - Recursive directory traversal
   - File metadata extraction
   - Support for .md, .markdown, .txt, .text extensions
3. ✅ Implemented `src/rag/chunker.py` - TextChunker with overlap
   - Configurable chunk size and overlap
   - Metadata preservation
   - Unique chunk ID generation
4. ✅ Created test fixtures - Sample documents (doc1.md, doc2.md, doc3.txt)
5. ✅ Written unit tests - 22 tests for loader and chunker (all passing)

### Phase 2: Vector Store ✅
6. ✅ Implemented `src/rag/store.py` - VectorStoreManager
   - FAISS flat and IVF index support
   - Document indexing with embeddings
   - Similarity search with L2 distance
   - Save/load to disk with pickle
   - Vector store statistics
7. ✅ Implemented `src/rag/retriever.py` - Retriever
   - Relevance threshold filtering
   - Context generation for LLM prompts
   - Source tracking and extraction
8. ✅ Written unit tests - 30 tests for store and retriever (all passing)
   - Mock embeddings for deterministic testing
   - Save/load persistence tests
   - Threshold and relevance filtering tests

**Test Results:**
- Total tests: 85 passing (83 unit + 2 contract)
  - Milestone 1: 31 tests
  - Milestone 2: 54 tests
- Code coverage: 82%
- No test failures

**Remaining Work (Phase 3):**
1. ⏳ Implement `src/rag/citations.py` - Citation formatting and tracking
2. ⏳ Implement `src/agent/rag_flow.py` - LangGraph workflow
   - State definition (RAGState)
   - Retrieve node
   - Synthesize node (LLM generation)
   - Cite node (add source references)
3. ⏳ Create integration test - End-to-end RAG flow
4. ⏳ Verify all Milestone 2 acceptance criteria

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

2. ~~**tiktoken build failure**~~ ✅ RESOLVED
   - tiktoken 0.12.0 installed successfully via wheel
   - Working with FAISS for embeddings in Milestone 2

3. ~~**Settings singleton in tests**~~ ✅ RESOLVED
   - Refactored tests to create fresh Settings instances

4. ~~**Missing entry point**~~ ✅ RESOLVED
   - Created src/main.py with FastAPI app initialization

**Current Issues:**
- None - all previous blockers resolved

---

## Dependencies Installed

- ✅ Core LangChain/LangGraph packages
- ✅ OpenAI and Anthropic provider packages
- ✅ FastAPI and Uvicorn
- ✅ SQLAlchemy and Alembic
- ✅ python-jose and PyJWT
- ✅ bcrypt (migrated from passlib)
- ✅ pytest and testing tools
- ✅ FAISS (faiss-cpu 1.13.2 - working)
- ✅ tiktoken (0.12.0 - working)

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
