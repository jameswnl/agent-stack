# Task List and Progress

Last Updated: 2026-03-14

## Active Tasks

### Task #1: Milestone 1 - Foundation and Contracts ✅ 90%

**Status:** IN PROGRESS
**Owner:** Implementation team
**Milestone:** Milestone 1

**Description:** Complete foundation setup including project scaffold, provider abstraction, database setup, authentication, and test infrastructure.

**Progress:**
- ✅ Project directory structure created
- ✅ pyproject.toml and requirements.txt created
- ✅ .env.example created
- ✅ Configuration module (settings.py) implemented
- ✅ Provider abstraction layer implemented (base, openai, anthropic, factory)
- ✅ Database models and CRUD implemented
- ✅ Authentication modules implemented (password hashing, JWT)
- ✅ Test fixtures and conftest.py created
- ✅ Unit tests written (config, providers, auth, db)
- ⏳ Fix test failures (bcrypt, settings isolation)
- ⏳ Create app bootstrap script
- ⏳ Verify database initialization works

**Blockers:**
- Some test failures due to:
  - bcrypt/passlib compatibility issue
  - Settings singleton not properly isolated in tests
- tiktoken can't be installed (needs Rust compiler, but not required for Milestone 1)

**Next Steps:**
1. Fix bcrypt test issue (upgrade bcrypt or adjust test data)
2. Refactor config tests to properly isolate Settings
3. Create src/main.py for app initialization
4. Verify all Milestone 1 acceptance criteria

---

### Task #2: Milestone 2 - RAG MVP ⏳

**Status:** PENDING
**Owner:** Unassigned
**Milestone:** Milestone 2
**Blocked By:** Task #1

**Description:** Implement document loading, chunking, FAISS indexing, retrieval, and basic LangGraph flow for RAG.

**Subtasks:**
- [ ] Document loader (Markdown/Text)
- [ ] Chunking strategy with metadata
- [ ] FAISS index manager
- [ ] Retrieval tool with relevance threshold
- [ ] LangGraph state definition
- [ ] LangGraph nodes (retrieve, synthesize, cite)
- [ ] Citation tracking
- [ ] Unit tests for all components
- [ ] Integration test: index -> query -> cited response

---

### Task #3: Milestone 3 - Authenticated API MVP ⏳

**Status:** PENDING
**Owner:** Unassigned
**Milestone:** Milestone 3
**Blocked By:** Task #2

**Description:** Implement FastAPI server with JWT authentication, user registration/login, user-scoped document indexing, and authenticated chat endpoint.

**Subtasks:**
- [ ] FastAPI server setup (server.py)
- [ ] Health endpoint
- [ ] Auth endpoints (register, login)
- [ ] Auth middleware and dependencies
- [ ] User-scoped document indexing endpoint
- [ ] Authenticated chat endpoint
- [ ] Integration tests with ephemeral database
- [ ] Test user data isolation

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
**Completed:** 2
**In Progress:** 1
**Pending:** 4
**Blocked:** 0

**Milestone 1 Progress:** 90%
**Overall Progress:** 13%

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
