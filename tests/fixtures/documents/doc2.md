# Vector Databases

Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently.

## Why Vector Databases?

Traditional databases work well for exact matches, but struggle with similarity search. Vector databases excel at finding semantically similar items.

## Popular Options

- **FAISS**: Facebook's library for efficient similarity search
- **Pinecone**: Managed vector database service
- **Weaviate**: Open-source vector search engine
- **Chroma**: Lightweight embedding database

## How They Work

Vector databases use specialized indexing structures like:

- HNSW (Hierarchical Navigable Small World)
- IVF (Inverted File Index)
- Product Quantization

These enable fast approximate nearest neighbor search even with millions of vectors.
