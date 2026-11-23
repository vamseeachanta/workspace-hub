"""Abstract base class for document parsers."""

from abc import ABC, abstractmethod
from pathlib import Path

from scripts.data.doc_intelligence.schema import DocumentManifest


class BaseParser(ABC):
    """Interface that every format-specific parser must implement."""

    @abstractmethod
    def can_handle(self, filepath: str) -> bool:
        """Return True if this parser supports the given file extension."""

    @abstractmethod
    def parse(self, filepath: str, domain: str) -> DocumentManifest:
        """Extract structure from the document and return a manifest."""
