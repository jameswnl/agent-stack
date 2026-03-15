# Milestone 2: RAG MVP - Implementation Plan

**Status:** IN PROGRESS
**Started:** 2026-03-14

## Overview

Build a working RAG (Retrieval-Augmented Generation) system that can:
- Load and chunk documents (Markdown/Text)
- Index them in a FAISS vector store
- Retrieve relevant chunks based on queries
- Generate cited answers using LangGraph

## Architecture

```
User Query
    ↓
LangGraph Workflow
    ↓
    ├─→ Retrieve (FAISS search)
    ├─→ Synthesize (LLM with context)
    └─→ Cite (Add source references)
    ↓
Cited Answer
```

## Components to Build

### 1. Document Loader (`src/rag/loader.py`)
- Load Markdown and Text files from directory
- Extract metadata (filename, path, modified date)
- Support recursive directory traversal
- Filter by file extensions

**Interface:**
```python
class DocumentLoader:
    def load_directory(path: str) -> List[Document]
    def load_file(path: str) -> Document
```

### 2. Text Chunker (`src/rag/chunker.py`)
- Split documents into chunks with overlap
- Preserve metadata on each chunk
- Configurable chunk size and overlap
- Markdown-aware splitting (preserve headers)

**Interface:**
```python
class TextChunker:
    def chunk_documents(docs: List[Document]) -> List[Chunk]
    def chunk_text(text: str, metadata: dict) -> List[Chunk]
```

### 3. Vector Store Manager (`src/rag/store.py`)
- FAISS index creation and persistence
- Document indexing with embeddings
- Similarity search with threshold
- Save/load index to disk

**Interface:**
```python
class VectorStoreManager:
    def index_documents(chunks: List[Chunk]) -> None
    def search(query: str, k: int, threshold: float) -> List[Chunk]
    def save(path: str) -> None
    def load(path: str) -> None
```

### 4. Retrieval Tool (`src/rag/retriever.py`)
- Wrapper around vector store
- Relevance threshold filtering
- Result formatting with scores

**Interface:**
```python
class Retriever:
    def retrieve(query: str, k: int = 5) -> List[RetrievalResult]
```

### 5. LangGraph Workflow (`src/agent/rag_flow.py`)
- State definition (query, context, answer, citations)
- Retrieve node (find relevant chunks)
- Synthesize node (generate answer with LLM)
- Cite node (add source references)

**State:**
```python
class RAGState(TypedDict):
    query: str
    retrieved_chunks: List[Chunk]
    context: str
    answer: str
    citations: List[Citation]
```

### 6. Citation Tracker (`src/rag/citations.py`)
- Extract source references
- Format citations
- Link chunks to sources

## Implementation Order

### Phase 1: Document Processing ✅
1. ✅ Create `src/rag/models.py` - Document, Chunk, Citation models
2. ✅ Implement `src/rag/loader.py` - Document loader
3. ✅ Implement `src/rag/chunker.py` - Text chunking
4. ✅ Write unit tests for loader and chunker

### Phase 2: Vector Store ⏳
5. ⏳ Implement `src/rag/store.py` - FAISS vector store
6. ⏳ Implement `src/rag/retriever.py` - Retrieval tool
7. ⏳ Write unit tests for store and retriever

### Phase 3: LangGraph Workflow ⏳
8. ⏳ Implement `src/agent/rag_flow.py` - LangGraph nodes
9. ⏳ Implement `src/rag/citations.py` - Citation formatting
10. ⏳ Write integration tests

### Phase 4: Testing & Verification ⏳
11. ⏳ Create test fixtures (sample documents)
12. ⏳ Integration test: index → query → cited response
13. ⏳ Verify acceptance criteria

## Dependencies

- ✅ langchain, langchain-core (already installed)
- ✅ langchain-openai (already installed)
- ⏳ faiss-cpu (need to install)
- ⏳ tiktoken (need to install)

## Test Strategy

- **Unit tests**: Each component in isolation with mocks
- **Integration tests**: Full flow with real FAISS (in-memory)
- **Fixtures**: Sample Markdown docs for testing
- **No network**: Mock LLM responses for deterministic tests

## Acceptance Criteria Checklist

- [ ] Documents can be indexed from a directory
- [ ] RAG query returns cited answer from indexed fixtures
- [ ] No external network dependency required for core tests
- [ ] All unit tests passing
- [ ] Integration test demonstrating full flow

## Files to Create

```
src/rag/
├── __init__.py (already exists)
├── models.py          # Document, Chunk, Citation models
├── loader.py          # Document loader
├── chunker.py         # Text chunking
├── store.py           # FAISS vector store manager
├── retriever.py       # Retrieval tool
└── citations.py       # Citation formatting

src/agent/
├── __init__.py (already exists)
└── rag_flow.py        # LangGraph workflow

tests/unit/
├── test_loader.py     # Document loader tests
├── test_chunker.py    # Chunking tests
├── test_store.py      # Vector store tests
└── test_retriever.py  # Retrieval tests

tests/integration/
└── test_rag_flow.py   # End-to-end RAG tests

tests/fixtures/
└── documents/         # Sample Markdown/Text files
    ├── doc1.md
    ├── doc2.md
    └── doc3.txt
```

## Estimated Effort

- Phase 1 (Document Processing): 2-3 hours
- Phase 2 (Vector Store): 2-3 hours
- Phase 3 (LangGraph): 2-3 hours
- Phase 4 (Testing): 1-2 hours

**Total: 7-11 hours**

## Notes

- FAISS installation may require special handling on some platforms
- tiktoken may need Rust compiler (can defer if issues)
- Keep chunk size reasonable (512-1024 tokens)
- Use OpenAI embeddings for now (already configured)
- LangGraph state management is key to the workflow

---

**Next Step:** Start with Phase 1 - Document Processing
