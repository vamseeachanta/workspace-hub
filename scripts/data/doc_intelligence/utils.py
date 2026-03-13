"""Utility functions — doc_ref generation, source availability check."""

import re
from pathlib import Path


def generate_doc_ref(filepath: str, doc_ref: str | None = None) -> str:
    """Derive a kebab-case doc_ref from filename, or use the override."""
    if doc_ref:
        return doc_ref
    name = Path(filepath).stem
    ref = name.lower()
    ref = ref.replace("_", "-")
    ref = re.sub(r"\s+", "-", ref)
    ref = re.sub(r"[^a-z0-9\-]", "", ref)
    ref = re.sub(r"-+", "-", ref).strip("-")
    return ref


def check_source_available(filepath: str) -> bool:
    """Return True if filepath exists and is a regular file."""
    p = Path(filepath)
    return p.is_file()
