"""Shared text utilities for promoters."""

import hashlib
import os
import re
from pathlib import Path


def sanitize_identifier(text: str) -> str:
    """Convert text to a valid Python/file identifier.

    Strips non-alphanumeric characters, collapses whitespace to underscores,
    lowercases, and ensures it doesn't start with a digit.

    >>> sanitize_identifier("Steel yield strength (MPa)")
    'steel_yield_strength_mpa'
    >>> sanitize_identifier("3.1 Some heading")
    '_3_1_some_heading'
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s_]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")
    if text and text[0].isdigit():
        text = "_" + text
    return text


def content_hash(content: str) -> str:
    """Return SHA-256 hex digest of content string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_atomic(path: Path, content: str, dry_run: bool = False) -> bool:
    """Write content atomically via temp file + rename.

    Compares existing file content byte-for-byte; skips if unchanged.
    Returns True if file was written, False if skipped.
    """
    path = Path(path)

    # Skip if file exists with identical content
    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
            if existing == content:
                return False
        except (OSError, UnicodeDecodeError):
            pass

    if dry_run:
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    return True


def source_citation(source: dict) -> str:
    """Format a source dict as a human-readable citation string.

    >>> source_citation({"document": "DNV-RP-B401.pdf", "section": "3.2", "page": 15})
    'DNV-RP-B401.pdf §3.2 p.15'
    >>> source_citation({"document": "foo.pdf"})
    'foo.pdf'
    """
    parts = [source.get("document", "unknown")]
    if source.get("section"):
        parts.append(f"§{source['section']}")
    if source.get("page"):
        parts.append(f"p.{source['page']}")
    if source.get("sheet"):
        parts.append(f"sheet:{source['sheet']}")
    return " ".join(parts)
