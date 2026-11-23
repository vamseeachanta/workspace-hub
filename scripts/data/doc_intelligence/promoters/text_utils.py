"""Shared text utilities for promoters."""

import hashlib
import os
import re
from pathlib import Path
from typing import Iterable, Optional


# Canonical doc_key form per
# docs/document-intelligence/standards-codes-provenance-reuse-contract.md §3:
# "<algorithm>:<lowercase-hex>" with namespace and hex length both load-bearing.
_DOC_KEY_ALGORITHMS = {
    "sha256": 64,
    # Legacy L1 registry compatibility only; new source_doc_key values should
    # use sha256 per the provenance-reuse contract.
    "md5": 32,
}
_DOC_KEY_RE = re.compile(r"^([a-z0-9]+):([a-f0-9]+)$")


class SourceDocKeyError(ValueError):
    """Raised when a record's source_doc_key violates the canonical contract.

    Carries a structured ``reason`` slug so callers can route on the failure
    mode without parsing the human message.
    """

    def __init__(self, reason: str, value: object, detail: str = "") -> None:
        self.reason = reason
        self.value = value
        msg = f"source_doc_key invalid ({reason}): {value!r}"
        if detail:
            msg = f"{msg} — {detail}"
        super().__init__(msg)


def validate_source_doc_key(
    value: object,
    *,
    output_content_hash: Optional[str] = None,
) -> str:
    """Validate a source_doc_key against the canonical contract.

    The contract (see Section 3 + 8.3 of the provenance-reuse doc):
    - Form is ``<algorithm>:<lowercase-hex>``.
    - Algorithm is sha256; md5 is accepted only for legacy L1 records.
    - Hex length matches the algorithm's digest length.
    - The value MUST NOT contain path separators, whitespace, or uppercase.
    - The value MUST NOT equal the promoted artifact's own content_hash
      (``sha256:<output_content_hash>``); that would be a self-loop where the
      artifact claims to be its own source.

    Returns the validated value unchanged on success.
    Raises :class:`SourceDocKeyError` on any violation.
    """
    if value is None:
        raise SourceDocKeyError("missing", value, "expected <algorithm>:<hex>")
    if not isinstance(value, str):
        raise SourceDocKeyError("type", value, "expected str")
    if not value:
        raise SourceDocKeyError("empty", value)

    # Reject path-like or whitespace-bearing strings up front so the regex
    # error message stays focused on canonical-form violations.
    if any(ch in value for ch in ("/", "\\", " ", "\t", "\n")):
        raise SourceDocKeyError(
            "path_or_whitespace", value,
            "doc_key must not contain path separators or whitespace",
        )
    if value != value.lower():
        raise SourceDocKeyError("case", value, "doc_key must be lowercase")

    match = _DOC_KEY_RE.fullmatch(value)
    if match is None:
        raise SourceDocKeyError(
            "format", value, "expected <algorithm>:<lowercase-hex>",
        )

    algorithm, hex_part = match.group(1), match.group(2)
    expected_len = _DOC_KEY_ALGORITHMS.get(algorithm)
    if expected_len is None:
        raise SourceDocKeyError(
            "algorithm", value,
            f"unknown algorithm {algorithm!r}; "
            f"allowed: {sorted(_DOC_KEY_ALGORITHMS)}",
        )
    if len(hex_part) != expected_len:
        raise SourceDocKeyError(
            "hex_length", value,
            f"expected {expected_len} hex chars for {algorithm}, "
            f"got {len(hex_part)}",
        )

    if output_content_hash is not None:
        if value == f"sha256:{output_content_hash}":
            raise SourceDocKeyError(
                "self_loop", value,
                "source_doc_key equals the promoted artifact's own "
                "content-hash; an artifact cannot be its own source",
            )

    return value


def extract_source_doc_key(record: dict) -> str:
    """Pull ``source.doc_key`` from a promoter input record, validating form.

    Does NOT apply the self-loop check; callers run that after computing the
    output body hash.
    """
    source = record.get("source") or {}
    raw = source.get("doc_key") if isinstance(source, dict) else None
    return validate_source_doc_key(raw)


def format_source_doc_key_header(keys: Iterable[str]) -> str:
    """Render one or more validated source_doc_keys as comment header lines.

    Always emits the singular ``# source_doc_key:`` field name (per Section 8.3
    of the contract) — multiple distinct keys produce multiple comment lines,
    one per key, sorted for determinism.
    """
    unique = sorted({k for k in keys if k})
    if not unique:
        return ""
    return "\n".join(f"# source_doc_key: {k}" for k in unique)


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
