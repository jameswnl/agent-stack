# Milestone Status

Last Updated: 2026-03-16 (M4 complete)

## Current Milestone: Milestone 4 - Research Extensions

**Status: 100% Complete** ✅

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

## Milestone 2: RAG MVP (Complete)

**Status: 100% Complete** ✅

**Deliverables:**
- ✅ Document loader for Markdown/Text (Phase 1)
- ✅ Chunking strategy with metadata preservation (Phase 1)
- ✅ FAISS index manager (Phase 2)
- ✅ Retrieval tool with relevance threshold (Phase 2)
- ✅ Citation tracking (Phase 3)
- ✅ LangGraph flow: retrieve -> synthesize -> cite (Phase 3)

**Acceptance Criteria:**
- ✅ Documents can be indexed from a directory
- ✅ RAG query returns cited answer from indexed fixtures
- ✅ No external network dependency required for core tests

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
- Total tests: 94 passing (88 unit + 3 integration + 2 contract + 1 other)
  - Milestone 1: 31 tests
  - Milestone 2: 63 tests (54 unit + 6 citations + 3 integration)
- Code coverage: 84%
- No test failures

### Phase 3: LangGraph Workflow ✅ (100% Complete)
9. ✅ Implemented `src/rag/citations.py` - Citation formatting and tracking
   - `build_citations()` - Extract from retrieval results
   - `format_citations()` - Numbered/unnumbered formatting
   - Deduplication by source+chunk_id
10. ✅ Implemented `src/agent/rag_flow.py` - LangGraph workflow
   - RAGState TypedDict definition
   - Retrieve node (search vector store)
   - Synthesize node (LLM generation with placeholder fallback)
   - Cite node (build citations)
   - RAGFlow class wrapper
   - create_rag_graph() factory function
11. ✅ Created integration tests - `tests/integration/test_rag_flow.py` (3 tests)
   - End-to-end RAG pipeline test
   - Citation verification
   - Graph compilation test
12. ✅ Created unit tests - `tests/unit/test_citations.py` (6 tests)
   - Citation building and formatting
   - Deduplication logic
   - Edge cases (empty results)
13. ✅ Verified all Milestone 2 acceptance criteria

**Next Milestone: Milestone 3 - Authenticated API MVP**

---

## Milestone 3: Authenticated API MVP (Complete)

**Status: 100% Complete** ✅

**Deliverables:**
- ✅ User registration/login endpoints
- ✅ JWT authentication middleware
- ✅ User-scoped document indexing
- ✅ Authenticated chat endpoint with RAG
- ✅ Multi-user data isolation
- ✅ API documentation (FastAPI auto-generated)

**Acceptance Criteria:**
- ✅ Unauthenticated requests are rejected
- ✅ User A cannot retrieve User B content
- ✅ API integration tests pass with ephemeral test database
- ✅ Conversation persistence deferred (stateless MVP per Decision 1)

**Completed Work:**

### API Layer ✅
1. ✅ Created `src/api/dependencies.py` - JWT authentication dependency
   - HTTPBearer token extraction
   - JWT verification via `verify_token`
   - Active user validation
2. ✅ Created `src/api/models.py` - Request/response models
   - RegisterRequest, LoginRequest, TokenResponse, UserResponse
   - IndexDocumentsRequest/Response
   - ChatRequest/Response with CitationResponse
3. ✅ Created `src/api/routes/auth.py` - Authentication endpoints
   - POST /api/v1/auth/register (201 on success)
   - POST /api/v1/auth/login
   - GET /api/v1/auth/me (protected)
4. ✅ Created `src/api/routes/documents.py` - Document indexing
   - POST /api/v1/documents/index (protected)
   - User-scoped FAISS store persistence
   - **Security: Path traversal protection** via `resolve_allowed_source_path`
5. ✅ Created `src/api/routes/chat.py` - Authenticated RAG chat
   - POST /api/v1/chat (protected)
   - User-scoped vector store loading
   - Graceful fallback when LLM unavailable
6. ✅ Created `src/api/routes/health.py` - Health check
   - GET /health (public)
7. ✅ Created `src/api/services.py` - Shared API helpers
   - `get_embeddings()`, `get_chat_model()`
   - `get_user_store_path()` - User isolation
   - `get_embedding_dimension()` - DRY helper
   - `resolve_allowed_source_path()` - **Security validation**

### Configuration & Security ✅
8. ✅ Updated `src/config/settings.py` - Configurable directories
   - `user_data_dir` (default: "data/users")
   - `ingest_base_dir` (default: "data/uploads")
9. ✅ Updated `src/main.py` - Application initialization
   - Router registration (health, auth, documents, chat)
   - Directory creation with absolute path resolution
   - `app.state.user_data_dir` and `app.state.ingest_base_dir`

### Testing ✅
10. ✅ Created `tests/integration/test_api_auth.py` - Comprehensive API tests (5 tests)
    - `test_register_login_and_me` - Auth flow
    - `test_protected_routes_require_auth` - Authorization enforcement
    - `test_index_and_chat_flow` - Index → query workflow
    - `test_user_document_isolation` - **Critical: User data isolation**
    - `test_index_rejects_source_path_outside_allowed_base` - **Security test**
11. ✅ Extracted `MockEmbeddings` to `tests/conftest.py` - DRY improvement
12. ✅ Updated existing tests to use shared `MockEmbeddings` fixture

**Security Improvements:**
- ✅ Path traversal vulnerability fixed (PR review critical issue)
- ✅ Server-side path validation with `resolve_allowed_source_path()`
- ✅ Configurable ingest base directory with absolute path resolution
- ✅ Integration test verifies rejection of paths outside allowed base

**Test Results:**
- Total tests: 99 passing (5 new integration tests)
  - Milestone 1: 31 tests
  - Milestone 2: 63 tests
  - Milestone 3: 5 integration tests
- All tests passing ✅
- No test failures

**PR:** #3 - Merged 2026-03-16

**Next Milestone: Milestone 4 - Research Extensions**

---

## Milestone 4: Research Extensions (Complete)

**Status: 100% Complete** ✅

**Deliverables:**
- ✅ Web search adapter behind tool interface
- ✅ Citation tracker for mixed-source responses
- ✅ Research planner for multi-step tasks
- ✅ Optional synthesis path combining RAG + web
- ✅ Design for hybrid retrieval across shared + user corpora

**Acceptance Criteria:**
- ✅ Planner selects tools based on query class
- ✅ Mixed-source responses preserve source attribution
- ✅ All external integrations have mocked contract tests and opt-in live tests

**Completed Work:**

### Tool Interface ✅
1. ✅ Created `src/tools/base.py` - Abstract search tool interface
   - `BaseSearchTool` ABC with `search()` method
   - `SearchResult` model (title, url, content, score, source_type)
2. ✅ Created `src/tools/web_search.py` - Tavily web search adapter
   - Client injection for testability without tavily package
   - Normalises Tavily response into `SearchResult` objects

### Research Planner ✅
3. ✅ Created `src/research/planner.py` - Query classifier
   - `QueryClass` enum: `RAG_ONLY`, `WEB_ONLY`, `MIXED`
   - Keyword-based classification (no LLM call needed)
   - `requested_class` vs `query_class` for consistent metadata after fallback
   - Graceful fallback when tools unavailable

### Mixed-Source Citations ✅
4. ✅ Created `src/research/citations.py` - Mixed citation tracker
   - Merges RAG + web results into unified citation list
   - Deduplication by (source, chunk_id/url)
   - Preserves `source_type` in metadata (rag/web)

### LangGraph Research Flow ✅
5. ✅ Created `src/agent/research_flow.py` - Research workflow
   - `plan -> retrieve + web_search -> synthesize -> cite`
   - Parallel fan-out for retrieve and web_search nodes
   - Context built from single retrieval pass (no double-fetch)
   - Works with RAG only, web only, both, or neither

### Design Document ✅
6. ✅ Created `docs/hybrid-retrieval-design.md`
   - Two-tier store model (shared + user)
   - Hybrid retriever with merge/dedup/re-rank
   - Access control and migration path
   - Deferred to Milestone 5 implementation

### Testing ✅
7. ✅ 31 new tests (9 planner, 5 web search, 9 mixed citations, 5 contract, 4 integration)
8. ✅ 1 opt-in live test (skipped without TAVILY_API_KEY)

**Review Fixes Applied:**
- ✅ Client injection for TavilySearchTool (works without tavily package)
- ✅ Single retrieval pass in research flow (no context divergence)
- ✅ Split requested_class vs query_class in planner

**Test Results:**
- Total tests: 133 passed, 1 skipped (live Tavily)
  - Milestone 1: 31 tests
  - Milestone 2: 63 tests
  - Milestone 3: 5 tests
  - Milestone 4: 31 tests + 5 contract
- All tests passing ✅

**PR:** #4 - Merged 2026-03-16

**Next Milestone: Milestone 5 - Advanced Operations**

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
