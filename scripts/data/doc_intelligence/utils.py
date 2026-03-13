"""Utility functions — doc_ref generation, source availability check."""

import hashlib
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


def generate_doc_ref_from_url(url: str, title: str | None = None) -> str:
    """Derive a doc_ref from a URL hash and optional title.

    Format: {sha256(url)[:8]}-{kebab(title)[:60]}
    """
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
    if not title:
        return url_hash
    slug = title.lower()
    slug = slug.replace("_", "-")
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    slug = slug[:60]
    return f"{url_hash}-{slug}"


def check_source_available(filepath: str) -> bool:
    """Return True if filepath exists and is a regular file."""
    p = Path(filepath)
    return p.is_file()
