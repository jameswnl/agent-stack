---
**IMPLEMENTATION STATUS - Last Updated: 2026-03-16**

**Current Milestone:** Milestone 4 - Research Extensions (Not Started)

**Quick Status:**
- ✅ Milestone 1: 100% complete (Foundation and Contracts)
- ✅ Milestone 2: 100% complete (RAG MVP)
- ✅ Milestone 3: 100% complete (Authenticated API MVP)
- ⏳ Milestone 4: 0% complete (Research Extensions)
- ⏳ Milestone 5: 0% complete (Advanced Operations)

**Overall Progress:** 60% (3 of 5 milestones complete)

**See:** `MILESTONE_STATUS.md`, `TASKS.md` for detailed progress

---

# LangGraph RAG + Research Service - Revised Implementation Plan

<!--
Review note:
This plan replaces the original "build everything at once" structure with staged delivery.
Reason: the latest source draft improved a few areas, notably explicit `DATABASE_URL` handling and initial conversation modeling, but it still mixes MVP work, production hardening, and advanced integrations in the same early phases. That keeps schedule risk high and verification ambiguous.
-->

## Objectives

Build a service that supports:

1. RAG over internal Markdown/Text documents
2. Structured research workflows using approved tools
3. Configurable LLM providers behind a stable interface
4. HTTP API access with authenticated multi-user isolation

Success means the system is usable after the MVP phase, not only after all advanced features are complete.

<!--
Change reason:
The updated source plan still lists many requirements without defining a clear "usable" checkpoint.
This version introduces an explicit MVP threshold so the team can stop and assess earlier.
-->

## Review Summary

<!--
Core issue 1:
The source plan still treats MVP features, advanced research tooling, and production-hardening work as one critical path. That makes the schedule fragile and increases the chance of partial implementations across many areas instead of one usable system.
-->

<!--
Core issue 2:
The source plan still mixes strict TDD expectations with early external-service dependencies such as provider SDKs, Tavily, and MCP. Without a hard split between mocked contract tests and opt-in live tests, CI and developer workflows will be unreliable.
-->

<!--
Core issue 3:
The source plan improved persistence setup by adding explicit database configuration and conversation models, but it still does not clearly decide which persistence features are required for MVP. Conversation support is especially under-specified.
-->

<!--
Core issue 4:
The source plan still duplicates implementation detail in multiple places, especially around dependency/config ownership and endpoint behavior. That creates drift risk between the plan, the eventual `pyproject.toml`, and the runtime settings layer.
-->

<!--
Core issue 5:
The source plan still defines success too broadly. It needs separate completion criteria for MVP versus post-MVP capabilities so reviewers can tell what must ship first and what can land later.
-->

## Delivery Principles

- Deliver a working vertical slice first: ingest docs -> answer with citations -> serve via API
- Keep provider selection and vector store behind interfaces from day one
- Treat web search and MCP as optional capabilities, not core-path dependencies
- Use TDD for domain logic and contract tests for integrations
- Prefer deterministic tests with mocks over provider/network-dependent tests

<!--
Change reason:
The updated source plan still claims strict TDD while also depending early on external systems such as Tavily and MCP.
That combination is unstable unless external integrations are explicitly treated as mocked contract boundaries.
-->

## Scope Boundaries

### In Scope for MVP

- Provider abstraction for chat + embeddings
- Markdown/Text ingestion and chunking
- FAISS-backed retrieval
- LangGraph workflow for RAG-only answers with citations
- FastAPI endpoint for authenticated chat
- Per-user vector store isolation
- Basic conversation persistence

### Deferred Until Post-MVP

- Multi-step research planner
- Web search provider integration
- MCP live system access
- Streaming responses
- Admin user bootstrap flows
- Advanced error diagnosis/log analysis tools
- Provider hot-switching per request across all endpoints

<!--
Change reason:
The updated source plan now covers more infrastructure detail, but it still includes all of these in the critical path, which remains the main source of over-scoping.
Deferring them does not remove them; it makes the first release buildable and testable.
-->

## Architecture Decisions

### Core Packages

```text
src/
  agent/
  api/
  auth/
  config/
  db/
  providers/
  rag/
  research/
  tools/
```

### Stable Interfaces

- `providers.base.BaseLLMProvider`
  - `get_chat_model()`
  - `get_embeddings()`
- `rag.store.VectorStore`
  - `index_documents()`
  - `search()`
  - `save()`
  - `load()`
- `research.tool_registry.ToolExecutor`
  - execution boundary for optional tools

<!--
Change reason:
The original plan exposed concrete FAISS and provider details in too many places.
Defining narrow interfaces up front reduces rewrites when adding providers or replacing storage later.
-->

## Target Milestones

### Milestone 1: Foundation and Contracts

Deliverables:

- Python project scaffold
- configuration loading
- provider factory with OpenAI and Anthropic support
- test harness with fixtures and mocks
- database bootstrap and migration setup

Acceptance criteria:

- app boots locally
- provider config can be loaded from file + env
- unit tests pass for provider and config contracts

<!--
Change reason:
Database/migration setup is pulled forward because auth and conversations depend on it.
The original plan delayed persistence details while already depending on them in later API phases.
-->

### Milestone 2: RAG MVP

Deliverables:

- document loader for Markdown/Text
- chunking strategy with metadata preservation
- FAISS index manager
- retrieval tool with relevance threshold
- LangGraph flow: retrieve -> synthesize -> cite

Acceptance criteria:

- documents can be indexed from a directory
- RAG query returns cited answer from indexed fixtures
- no external network dependency required for core tests

<!--
Change reason:
This milestone creates a complete product slice before research tooling, auth hardening, or streaming.
The original plan split the core answer path across too many phases.
-->

### Milestone 3: Authenticated API MVP

Deliverables:

- JWT auth
- user registration/login
- user-scoped document indexing
- authenticated chat endpoint
- health endpoint
- conversation create/read support only if required by the API contract

Acceptance criteria:

- unauthenticated requests are rejected
- user A cannot retrieve user B content
- API integration tests pass with an ephemeral test database
- conversation persistence is either implemented end-to-end or explicitly deferred from MVP

<!--
Change reason:
The latest source draft adds conversation models, but it still does not clearly decide whether conversation persistence is an MVP requirement or just future scaffolding.
This milestone makes that decision explicit to avoid half-implementing it.
-->

<!--
Change reason:
The original plan introduced API and auth after a large amount of non-user-facing work.
This version moves the first real deployment surface earlier.
-->

### Milestone 4: Research Extensions

Deliverables:

- web search adapter behind tool interface
- citation tracker for mixed-source responses
- research planner for multi-step tasks
- optional synthesis path combining RAG + web

Acceptance criteria:

- planner selects tools based on query class
- mixed-source responses preserve source attribution
- all external integrations have mocked contract tests and opt-in live tests

<!--
Change reason:
Web search is moved behind a milestone boundary because it introduces temporal instability, cost, and flaky tests.
-->

### Milestone 5: Advanced Operations

Deliverables:

- MCP integration
- log analysis and error diagnosis tools
- streaming chat endpoint
- operational docs and deployment guidance

Acceptance criteria:

- MCP is optional and feature-flagged
- streaming endpoint emits valid SSE frames
- production checklist is documented

<!--
Change reason:
MCP and operational tooling are powerful but risky; they should not block the main service from shipping.
-->

## Implementation Sequence

1. Create project skeleton, dependency management, and config layer.
2. Implement provider contracts and provider factory.
3. Implement document loading, chunking, and vector store adapter.
4. Implement the minimal LangGraph RAG flow.
5. Add auth, persistence, and user-scoped indexing.
6. Expose the MVP through FastAPI.
7. Add research extensions behind feature flags.
8. Add advanced tools and streaming after the core path is stable.

<!--
Change reason:
This sequence removes circular dependencies in the original plan, where later components assumed APIs and persistence details that had not been properly stabilized.
-->

## Test Strategy

### Unit Tests

- config parsing and environment overrides
- provider factory behavior
- document loading and chunk metadata
- vector store persistence/load
- auth token creation/verification
- user isolation path calculation

### Integration Tests

- index documents -> query -> cited response
- register/login -> index docs -> authenticated chat
- per-user data isolation

### Contract Tests

- provider adapter request/response shape
- web search adapter normalization
- MCP client protocol handling

### Live Tests

- opt-in only
- run separately from CI-required suites
- require explicit credentials and service availability
- never gate merges on Tavily, provider, or MCP uptime

<!--
Change reason:
The original plan mixed unit, integration, and live external tests without a clear boundary.
That makes CI policy unclear and will lead to unstable pipelines.
-->

## Proposed Repository Layout

```text
src/
  agent/
    graph.py
    nodes.py
    state.py
  api/
    server.py
    dependencies.py
    models.py
    routes/
      auth.py
      chat.py
      documents.py
      health.py
  auth/
    jwt.py
    password.py
  config/
    settings.py
    providers.py
  db/
    database.py
    models.py
    crud.py
  providers/
    base.py
    factory.py
    openai_provider.py
    anthropic_provider.py
  rag/
    documents.py
    chunking.py
    store.py
    retrieval.py
  research/
    planner.py
    citations.py
  tools/
    web_search.py
    mcp.py
    log_analysis.py
tests/
  unit/
  integration/
  contract/
  fixtures/
```

<!--
Change reason:
The layout is simplified and normalized. The original plan had overlapping concerns, for example config split between root files and source modules with no clear ownership.
-->

## Dependency Policy

- Pin major versions, not every patch version, in the plan document
- Keep the source of truth in `pyproject.toml`, not duplicated in multiple sections
- Avoid naming speculative versions in planning docs unless compatibility has been verified

Initial dependency groups:

- Core: `langgraph`, `langchain`, `langchain-core`, `pydantic`, `pydantic-settings`
- Providers: `langchain-openai`, `langchain-anthropic`
- RAG: `faiss-cpu`
- API/Auth/DB: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `python-jose`, `passlib[bcrypt]`
- Dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `ruff`, `mypy`

<!--
Change reason:
The original plan duplicated dependency lists and hardcoded many specific versions, creating drift risk inside the same document.
-->

## Configuration Plan

Use one typed settings module with environment overrides:

- `APP_ENV`
- `DATABASE_URL`
- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `JWT_SECRET_KEY`
- `TAVILY_API_KEY` only if web search is enabled

Keep provider-specific defaults in a dedicated provider config file or typed registry, not spread across route handlers.

<!--
Change reason:
The original plan leaks config loading into route logic and mixes runtime defaults across multiple files.
Centralizing settings reduces hidden behavior.
-->

## Risks and Mitigations

- Provider SDK churn
  - Mitigation: isolate adapters and use contract tests
- Retrieval quality is poor with naive chunking
  - Mitigation: benchmark chunking strategies before adding research tools
- User isolation bugs expose wrong documents
  - Mitigation: make user scope part of store API and integration-test it early
- External tools make CI flaky
  - Mitigation: keep them behind mocks and opt-in live suites
- MCP broadens security surface
  - Mitigation: feature-flag it and require explicit allowlists

<!--
Change reason:
The original plan had success criteria but no concrete risk register, which is a gap for a project involving auth, external tools, and user-isolated data.
-->

## Revised Timeline

- Day 1: Foundation and config
- Day 2: Provider abstraction and tests
- Day 3: Document ingestion and FAISS indexing
- Day 4: LangGraph RAG flow
- Day 5: Auth, DB, and user isolation
- Day 6: FastAPI MVP
- Day 7: Integration hardening and docs
- Day 8+: Research extensions
- Day 10+: MCP, streaming, and advanced tools

<!--
Change reason:
The original eight-day schedule treated MVP and advanced tooling as equal-confidence tasks.
This timeline separates committed work from contingent work.
-->

## Done Criteria

MVP is complete when:

- authenticated users can register, index their own docs, and chat against them
- responses include citations to indexed content
- provider selection is configurable without code changes
- core tests pass in CI without live external services

Full project is complete when:

- research workflows operate with cited mixed sources
- optional live integrations are covered by contract and opt-in live tests
- deployment and operational docs exist

<!--
Change reason:
The original "success criteria" list was broad but did not distinguish shipping criteria from aspirational completeness.
-->

## Immediate Next Steps

1. Approve the milestone boundaries and deferred items.
2. Convert Milestone 1 into tracked issues/tasks.
3. Decide whether conversation persistence is required in MVP or can be reduced to stateless chat.
4. Start with provider/config contracts and test fixtures.

<!--
Change reason:
This closes with decision points rather than generic setup commands, which is more useful for reviewers and implementers.
-->
