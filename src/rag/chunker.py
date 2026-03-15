"""Text chunking with metadata preservation."""

import hashlib
from typing import List, Dict, Any

from .models import Document, Chunk


class TextChunker:
    """Splits documents into chunks with overlap."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n\n"
    ):
        """Initialize text chunker.

        Args:
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            separator: Text separator for splitting (default: double newline)
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be greater than or equal to 0")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """Chunk multiple documents.

        Args:
            documents: List of documents to chunk

        Returns:
            List of chunks from all documents
        """
        all_chunks = []

        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)

        return all_chunks

    def chunk_document(self, document: Document) -> List[Chunk]:
        """Chunk a single document.

        Args:
            document: Document to chunk

        Returns:
            List of chunks from the document
        """
        return self.chunk_text(
            text=document.content,
            metadata=document.metadata,
            source=document.source
        )

    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] | None = None,
        source: str | None = None
    ) -> List[Chunk]:
        """Chunk raw text into smaller pieces.

        Args:
            text: Text to chunk
            metadata: Base metadata to include in all chunks
            source: Source identifier

        Returns:
            List of chunks
        """
        if not text.strip():
            return []

        metadata = metadata or {}
        source = source or "unknown"

        # Split text by separator first
        splits = self._split_text(text)

        # Combine splits into chunks with overlap
        chunks = []
        current_chunk = []
        current_size = 0

        for i, split in enumerate(splits):
            split_size = len(split)

            # If single split is larger than chunk_size, split it further
            if split_size > self.chunk_size:
                # Add current chunk if any
                if current_chunk:
                    chunk_text = "".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text,
                        len(chunks),
                        metadata,
                        source
                    ))
                    current_chunk = []
                    current_size = 0

                # Split large text by character count
                for j in range(0, split_size, self.chunk_size - self.chunk_overlap):
                    chunk_text = split[j:j + self.chunk_size]
                    if chunk_text.strip():
                        chunks.append(self._create_chunk(
                            chunk_text,
                            len(chunks),
                            metadata,
                            source
                        ))
                continue

            # Check if adding this split would exceed chunk_size
            if current_size + split_size > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk_text = "".join(current_chunk)
                chunks.append(self._create_chunk(
                    chunk_text,
                    len(chunks),
                    metadata,
                    source
                ))

                # Start new chunk with overlap
                overlap_size = 0
                overlap_chunks = []

                # Add previous splits for overlap
                for prev_split in reversed(current_chunk):
                    if overlap_size + len(prev_split) <= self.chunk_overlap:
                        overlap_chunks.insert(0, prev_split)
                        overlap_size += len(prev_split)
                    else:
                        break

                current_chunk = overlap_chunks
                current_size = overlap_size

            # Add split to current chunk
            current_chunk.append(split)
            current_size += split_size

        # Add final chunk
        if current_chunk:
            chunk_text = "".join(current_chunk)
            chunks.append(self._create_chunk(
                chunk_text,
                len(chunks),
                metadata,
                source
            ))

        return chunks

    def _split_text(self, text: str) -> List[str]:
        """Split text by separator.

        Args:
            text: Text to split

        Returns:
            List of text segments
        """
        if self.separator:
            # Split by separator but keep it
            splits = text.split(self.separator)
            # Add separator back except for last split
            result = []
            for i, split in enumerate(splits):
                if i < len(splits) - 1:
                    result.append(split + self.separator)
                else:
                    result.append(split)
            return [s for s in result if s.strip()]
        else:
            return [text]

    def _create_chunk(
        self,
        text: str,
        index: int,
        base_metadata: Dict[str, Any],
        source: str
    ) -> Chunk:
        """Create a chunk with metadata.

        Args:
            text: Chunk text
            index: Chunk index
            base_metadata: Base metadata from document
            source: Source identifier

        Returns:
            Chunk object
        """
        # Generate unique chunk ID
        chunk_id = self._generate_chunk_id(source, index)

        # Combine metadata
        metadata = {
            **base_metadata,
            "chunk_index": index,
            "chunk_size": len(text),
            "source": source,
        }

        return Chunk(
            content=text.strip(),
            metadata=metadata,
            chunk_id=chunk_id
        )

    def _generate_chunk_id(self, source: str, index: int) -> str:
        """Generate unique chunk ID.

        Args:
            source: Source identifier
            index: Chunk index

        Returns:
            Unique chunk ID
        """
        # Create hash from source and index
        content = f"{source}:{index}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:16]
