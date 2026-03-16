# Hybrid Retrieval Design: Shared + User Corpora

## Status

**Design only** — implementation planned for Milestone 5.

## Problem

Currently each user has an isolated FAISS vector store. This is correct for data isolation but creates two issues:

1. **Duplication** — Common documentation (e.g. product docs, FAQs) is re-indexed per user.
2. **Freshness** — Each user must independently index shared content.

## Proposed Architecture

### Two-tier Store Model

```
┌──────────────────────────────────────┐
│            Retriever                 │
│  ┌────────────┐  ┌───────────────┐  │
│  │ User Store  │  │ Shared Store  │  │
│  │ (per-user)  │  │  (global)     │  │
│  └────────────┘  └───────────────┘  │
│         ↓               ↓           │
│       merge + deduplicate + rank     │
└──────────────────────────────────────┘
```

### Components

1. **Shared Store** — A single FAISS index holding common documentation. Managed by admin users or a background process.

2. **User Store** — Per-user FAISS index (existing implementation). Holds user-uploaded private documents.

3. **Hybrid Retriever** — Queries both stores, merges results, deduplicates by chunk content hash, and re-ranks by score.

### Retrieval Flow

```
query
  ├── search(shared_store, k=N)  → shared_results
  ├── search(user_store, k=N)    → user_results
  └── merge(shared_results, user_results)
        ├── deduplicate by content hash
        ├── re-rank by score
        └── tag each result with scope: "shared" | "private"
```

### Citation Scope

Each citation will include a `scope` field in metadata:

```python
Citation(
    source="product-docs/setup.md",
    metadata={
        "source_type": "rag",
        "scope": "shared",   # or "private"
    }
)
```

This allows the UI to visually distinguish shared vs. private sources.

### Access Control

- **Shared store**: Read-only for all authenticated users. Write access restricted to admin role.
- **User store**: Read/write scoped to the owning user (existing behavior).
- **No cross-user access**: A user's private store is never queried by another user.

### API Changes

The `/api/v1/chat` endpoint would accept an optional `include_shared: bool = True` parameter to let users opt out of shared results.

A new admin endpoint would handle shared corpus management:

```
POST /api/v1/admin/index   — Index documents into the shared store
GET  /api/v1/admin/stats   — Shared store statistics
```

### Migration Path

1. Add `SharedVectorStoreManager` that wraps the existing `VectorStoreManager` with a fixed path.
2. Create `HybridRetriever` that delegates to two retrievers and merges results.
3. Update `ResearchFlow` to accept an optional shared retriever.
4. Add admin endpoints behind a role check.

### Risks

- **Result quality**: Merging results from two stores with different embedding distributions could produce inconsistent ranking. Mitigation: normalize scores before merging.
- **Duplicate content**: If a user indexes the same doc that exists in shared store, both copies appear. Mitigation: deduplicate by content hash.
- **Storage**: Shared store grows with common docs. Mitigation: periodic reindexing with dedup.

## Decision

Implement in Milestone 5 after the core research flow is stable. The current per-user isolation model is sufficient for MVP and post-MVP research features.
