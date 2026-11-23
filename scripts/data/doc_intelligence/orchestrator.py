"""Format detection and parser dispatch for document extraction."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from scripts.data.doc_intelligence.parsers import get_parser
from scripts.data.doc_intelligence.schema import (
    DocumentManifest,
    DocumentMetadata,
    write_manifest,
)


def _compute_checksum(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()


def extract_document(
    filepath: str,
    domain: str,
    output: Optional[str] = None,
    doc_ref: Optional[str] = None,
) -> DocumentManifest:
    """Detect format, dispatch to parser, optionally write manifest."""
    p = Path(filepath)
    parser = get_parser(filepath)

    if parser is None:
        ext = p.suffix
        meta = DocumentMetadata(
            filename=p.name,
            format=ext.lstrip(".") if ext else "unknown",
            size_bytes=p.stat().st_size if p.exists() else 0,
            checksum=_compute_checksum(filepath) if p.exists() else None,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        manifest = DocumentManifest(
            version="1.0.0",
            tool="extract-document/1.0.0",
            domain=domain,
            metadata=meta,
            doc_ref=doc_ref,
            errors=[f"Unsupported format: {ext or 'no extension'}"],
            extraction_stats={"sections": 0, "tables": 0, "figure_refs": 0},
        )
    else:
        manifest = parser.parse(filepath, domain)
        manifest.doc_ref = doc_ref

    if output:
        write_manifest(manifest, Path(output))

    return manifest
