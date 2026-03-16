# Task List and Progress

Last Updated: 2026-03-16

## Active Tasks

---

### Task #4: Milestone 4 - Research Extensions ⏳

**Status:** PENDING
**Owner:** Unassigned
**Milestone:** Milestone 4
**Blocked By:** Task #3

**Description:** Add web search adapter, research planner, citation tracker, and mixed-source synthesis.

**Subtasks:**
- [ ] Web search adapter (Tavily) with mocked tests
- [ ] Research planner (query classification)
- [ ] Citation tracker for mixed sources
- [ ] Update LangGraph flow for mixed RAG + web
- [ ] Contract tests for web search
- [ ] Opt-in live tests with real Tavily API

---

### Task #5: Milestone 5 - Advanced Operations ⏳

**Status:** PENDING
**Owner:** Unassigned
**Milestone:** Milestone 5
**Blocked By:** Task #4

**Description:** MCP integration, log analysis, error diagnosis, streaming endpoints, operational docs.

**Subtasks:**
- [ ] MCP client implementation
- [ ] Log analysis tool
- [ ] Error diagnosis tool
- [ ] Streaming chat endpoint (SSE)
- [ ] Feature flags for optional tools
- [ ] Production deployment guide
- [ ] Operational runbook

---

## Completed Tasks

### Task #2: Milestone 2 - RAG MVP ✅

**Status:** COMPLETED
**Completed:** 2026-03-15
**Milestone:** Milestone 2

Completed full RAG system with document loading, FAISS indexing, retrieval, and LangGraph workflow.

**Deliverables:**
- ✅ Document loader and chunker (Phase 1)
- ✅ FAISS vector store and retriever (Phase 2)
- ✅ Citation tracker and LangGraph workflow (Phase 3)
- ✅ Integration tests (Phase 4)
- ✅ 63 tests passing (54 unit + 6 citations + 3 integration)

**Test Results:** 94 total tests, 84% coverage

**PR:** #1 - Merged 2026-03-15

---

### Task #3: Milestone 3 - Authenticated API MVP ✅

**Status:** COMPLETED
**Completed:** 2026-03-16
**Milestone:** Milestone 3

Completed authenticated API layer with user registration/login, JWT authentication, user-scoped document indexing, and authenticated RAG chat endpoint.

**Deliverables:**
- ✅ Authentication endpoints (register, login, me)
- ✅ JWT authentication dependency
- ✅ User-scoped document indexing with path security
- ✅ Authenticated RAG chat endpoint
- ✅ Multi-user data isolation
- ✅ 5 integration tests (auth flow, protected routes, index+chat, user isolation, security)

**Security:**
- ✅ Path traversal vulnerability fixed
- ✅ Server-side path validation with `resolve_allowed_source_path()`
- ✅ Configurable ingest base directory

**Test Results:** 99 total tests passing, 5 new integration tests

**PR:** #3 - Merged 2026-03-16

---

### Task #1: Milestone 1 - Foundation and Contracts ✅

**Status:** COMPLETED
**Completed:** 2026-03-14
**Milestone:** Milestone 1

Completed all foundation work including project scaffold, configuration, provider abstraction, database setup, authentication, and testing infrastructure.

**Deliverables:**
- ✅ Python project scaffold
- ✅ Configuration loading (settings.py)
- ✅ Provider factory (OpenAI, Anthropic)
- ✅ Database models and CRUD
- ✅ Authentication (bcrypt + JWT)
- ✅ Test harness with 31 passing tests
- ✅ FastAPI entry point (main.py)

**Test Results:** 31 tests passing, 71% coverage

---

### Task #6: Create pyproject.toml with all dependencies ✅

**Status:** COMPLETED
**Completed:** 2026-03-14

Created pyproject.toml with all required dependencies for Milestone 1-3, plus optional dependencies for Milestone 4+.

---

### Task #7: Create .env.example and config files ✅

**Status:** COMPLETED
**Completed:** 2026-03-14

Created .env.example with all environment variables and configuration templates.

---

## Task Metadata

**Total Tasks:** 7
**Completed:** 5 (Milestones 1, 2 & 3, pyproject.toml, .env.example)
**In Progress:** 0
**Pending:** 2 (Milestones 4, 5)
**Blocked:** 0

**Milestone Progress:**
- Milestone 1: 100% complete ✅
- Milestone 2: 100% complete ✅
- Milestone 3: 100% complete ✅
- Milestone 4: 0% (not started)
- Milestone 5: 0% (not started)

**Overall Project Progress:** ~60% (3 of 5 milestones complete)

---

## Decision Log

### Decision 1: Conversation Persistence - Option A Selected

**Date:** 2026-03-14
**Context:** Milestone 3 requires decision on conversation history
**Decision:** Implement stateless chat for MVP (Option A)
**Rationale:** Database models exist for schema stability, but CRUD operations are deferred to post-MVP to reduce scope

### Decision 2: Dependency Management - uv Selected

**Date:** 2026-03-14
**Context:** Poetry not available, need to choose pip or uv
**Decision:** Use uv for dependency installation
**Rationale:** Faster than pip, better dependency resolution

### Decision 3: Test Strategy - Separate Contract and Live Tests

**Date:** 2026-03-14
**Context:** Need to handle external service dependencies in tests
**Decision:** Use pytest markers: unit, integration, contract, live
**Rationale:** Keeps CI deterministic, allows opt-in testing of external services

---

## Next Session Checklist

To resume work in a new session:

1. **Navigate to project directory:**
   ```bash
   cd ~/ws/langgraph
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Review current status:**
   - Read `MILESTONE_STATUS.md` for milestone progress
   - Read `TASKS.md` for current task status
   - Read `IMPLEMENTATION_PLAN_REVISED.md` for overall plan

4. **Check what's blocking:**
   - Look at "Remaining Work" in MILESTONE_STATUS.md
   - Look at "Blockers" in TASKS.md

5. **Run tests to see current state:**
   ```bash
   PYTHONPATH=. pytest tests/unit/ -v -m unit
   ```

6. **Continue from Task #1 if incomplete, or move to Task #2**
