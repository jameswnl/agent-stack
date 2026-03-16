"""Document loader for Markdown and Text files."""

from datetime import datetime
from pathlib import Path
from typing import List, Set

from .models import Document


class DocumentLoader:
    """Loads documents from filesystem."""

    DEFAULT_EXTENSIONS = {".md", ".markdown", ".txt", ".text"}

    def __init__(self, extensions: Set[str] | None = None):
        """Initialize document loader.

        Args:
            extensions: File extensions to load (default: .md, .markdown, .txt, .text)
        """
        self.extensions = extensions or self.DEFAULT_EXTENSIONS

    def load_directory(
        self, directory_path: str, recursive: bool = True, glob_pattern: str | None = None
    ) -> List[Document]:
        """Load all documents from a directory.

        Args:
            directory_path: Path to directory containing documents
            recursive: Whether to search subdirectories
            glob_pattern: Optional glob pattern to filter files

        Returns:
            List of loaded documents

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        path = Path(directory_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        documents = []

        # Use glob pattern if provided, otherwise search by extensions
        if glob_pattern:
            files = path.rglob(glob_pattern) if recursive else path.glob(glob_pattern)
        else:
            # Find all files with matching extensions
            files = []
            if recursive:
                for ext in self.extensions:
                    files.extend(path.rglob(f"*{ext}"))
            else:
                for ext in self.extensions:
                    files.extend(path.glob(f"*{ext}"))

        for file_path in files:
            if file_path.is_file():
                try:
                    doc = self.load_file(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    # Log error but continue loading other files
                    print(f"Warning: Failed to load {file_path}: {e}")

        return documents

    def load_file(self, file_path: str) -> Document:
        """Load a single document file.

        Args:
            file_path: Path to document file

        Returns:
            Loaded document

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file extension not supported
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Check extension
        if path.suffix.lower() not in self.extensions:
            raise ValueError(f"Unsupported file extension: {path.suffix}. Supported: {', '.join(self.extensions)}")

        # Read file content
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get file stats
        stats = path.stat()

        # Build metadata
        metadata = {
            "filename": path.name,
            "file_path": str(path.absolute()),
            "file_size": stats.st_size,
            "file_extension": path.suffix,
            "modified_time": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "created_time": datetime.fromtimestamp(stats.st_ctime).isoformat(),
        }

        return Document(content=content, metadata=metadata, source=str(path.absolute()))

    def load_files(self, file_paths: List[str]) -> List[Document]:
        """Load multiple document files.

        Args:
            file_paths: List of file paths to load

        Returns:
            List of loaded documents
        """
        documents = []

        for file_path in file_paths:
            try:
                doc = self.load_file(file_path)
                documents.append(doc)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

        return documents
