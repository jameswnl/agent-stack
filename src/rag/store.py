"""FAISS vector store manager for document indexing and retrieval."""

import pickle
from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np
from langchain_core.embeddings import Embeddings

from .models import Chunk, RetrievalResult


class VectorStoreManager:
    """Manages FAISS vector store for document chunks."""

    def __init__(
        self,
        embeddings: Embeddings,
        dimension: int = 1536,  # Default for OpenAI text-embedding-3-small
        index_type: str = "flat",
    ):
        """Initialize vector store manager.

        Args:
            embeddings: Embeddings model to use
            dimension: Vector dimension (depends on embedding model)
            index_type: FAISS index type ("flat" or "ivf")
        """
        self.embeddings = embeddings
        self.dimension = dimension
        self.index_type = index_type

        # Initialize FAISS index
        self.index: Optional[faiss.Index] = None
        self.chunks: List[Chunk] = []

        self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize FAISS index based on type."""
        if self.index_type == "flat":
            # Flat index for exact search
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # IVF index for faster approximate search
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")

    def index_documents(self, chunks: List[Chunk]) -> None:
        """Index document chunks into vector store.

        Args:
            chunks: List of chunks to index
        """
        if not chunks:
            return

        # Generate embeddings for all chunks
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embeddings.embed_documents(texts)

        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Train index if needed (for IVF)
        if self.index_type == "ivf" and not self.index.is_trained:
            self.index.train(embeddings_array)

        # Add vectors to index
        self.index.add(embeddings_array)

        # Store chunks with embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            self.chunks.append(chunk)

    def search(self, query: str, k: int = 5, threshold: Optional[float] = None) -> List[RetrievalResult]:
        """Search for similar chunks.

        Args:
            query: Query text
            k: Number of results to return
            threshold: Optional similarity threshold (L2 distance)

        Returns:
            List of retrieval results sorted by relevance
        """
        if not self.chunks:
            return []

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        query_array = np.array([query_embedding], dtype=np.float32)

        # Search index
        distances, indices = self.index.search(query_array, k)

        # Build results
        results = []
        for rank, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            # Check if index is valid
            if idx == -1 or idx >= len(self.chunks):
                continue

            # Apply threshold if specified (lower distance is better for L2)
            if threshold is not None and distance > threshold:
                continue

            # Convert L2 distance to similarity score (0-1, higher is better)
            # Using exponential decay: score = exp(-distance)
            score = float(np.exp(-distance))

            result = RetrievalResult(chunk=self.chunks[idx], score=score, rank=rank)
            results.append(result)

        return results

    def save(self, directory_path: str) -> None:
        """Save vector store to disk.

        Args:
            directory_path: Directory to save index and chunks
        """
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = path / "index.faiss"
        faiss.write_index(self.index, str(index_path))

        # Save chunks
        chunks_path = path / "chunks.pkl"
        with open(chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)

        # Save metadata
        metadata_path = path / "metadata.pkl"
        metadata = {
            "dimension": self.dimension,
            "index_type": self.index_type,
            "num_chunks": len(self.chunks),
        }
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)

    def load(self, directory_path: str) -> None:
        """Load vector store from disk.

        Args:
            directory_path: Directory containing saved index and chunks

        Raises:
            FileNotFoundError: If directory or files don't exist
        """
        path = Path(directory_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Load FAISS index
        index_path = path / "index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        self.index = faiss.read_index(str(index_path))

        # Load chunks
        chunks_path = path / "chunks.pkl"
        if not chunks_path.exists():
            raise FileNotFoundError(f"Chunks file not found: {chunks_path}")

        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)

        # Load metadata (optional, for verification)
        metadata_path = path / "metadata.pkl"
        if metadata_path.exists():
            with open(metadata_path, "rb") as f:
                pickle.load(f)  # loaded for future verification

    def clear(self) -> None:
        """Clear the vector store."""
        self._initialize_index()
        self.chunks = []

    def get_stats(self) -> dict:
        """Get vector store statistics.

        Returns:
            Dictionary with store statistics
        """
        return {
            "num_chunks": len(self.chunks),
            "index_type": self.index_type,
            "dimension": self.dimension,
            "is_trained": self.index.is_trained if hasattr(self.index, "is_trained") else True,
            "total_vectors": self.index.ntotal,
        }
