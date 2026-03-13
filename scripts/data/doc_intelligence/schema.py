"""Manifest dataclasses and serialization for document extraction."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class SourceLocation:
    """Where an extracted element came from."""

    document: str
    section: Optional[str] = None
    page: Optional[int] = None
    sheet: Optional[str] = None


@dataclass
class ExtractedSection:
    """A text block with optional heading."""

    heading: Optional[str]
    level: int  # 0=body, 1-6=heading level
    text: str
    source: SourceLocation


@dataclass
class ExtractedTable:
    """A table with column headers and rows."""

    title: Optional[str]
    columns: List[str]
    rows: List[List[str]]
    source: SourceLocation


@dataclass
class ExtractedFigureRef:
    """A reference to a figure found in the document."""

    caption: Optional[str]
    figure_id: Optional[str]
    source: SourceLocation


@dataclass
class DocumentMetadata:
    """Document-level metadata."""

    filename: str
    format: str
    size_bytes: int
    pages: Optional[int] = None
    sheets: Optional[int] = None
    checksum: Optional[str] = None
    extraction_timestamp: Optional[str] = None


@dataclass
class DocumentManifest:
    """Top-level extraction manifest."""

    version: str
    tool: str
    domain: str
    metadata: DocumentMetadata
    doc_ref: Optional[str] = None
    sections: List[ExtractedSection] = field(default_factory=list)
    tables: List[ExtractedTable] = field(default_factory=list)
    figure_refs: List[ExtractedFigureRef] = field(default_factory=list)
    extraction_stats: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


# -- Serialization helpers --------------------------------------------------


def _source_to_dict(s: SourceLocation) -> dict:
    d = {"document": s.document}
    if s.section is not None:
        d["section"] = s.section
    if s.page is not None:
        d["page"] = s.page
    if s.sheet is not None:
        d["sheet"] = s.sheet
    return d


def _source_from_dict(d: dict) -> SourceLocation:
    return SourceLocation(
        document=d["document"],
        section=d.get("section"),
        page=d.get("page"),
        sheet=d.get("sheet"),
    )


def manifest_to_dict(m: DocumentManifest) -> dict:
    """Convert a DocumentManifest to a plain dict for YAML serialization."""
    meta = {
        "filename": m.metadata.filename,
        "format": m.metadata.format,
        "size_bytes": m.metadata.size_bytes,
    }
    if m.metadata.pages is not None:
        meta["pages"] = m.metadata.pages
    if m.metadata.sheets is not None:
        meta["sheets"] = m.metadata.sheets
    if m.metadata.checksum is not None:
        meta["checksum"] = m.metadata.checksum
    if m.metadata.extraction_timestamp is not None:
        meta["extraction_timestamp"] = m.metadata.extraction_timestamp

    result = {
        "version": m.version,
        "tool": m.tool,
        "domain": m.domain,
    }
    if m.doc_ref is not None:
        result["doc_ref"] = m.doc_ref
    result["metadata"] = meta
    return {
        **result,
        "sections": [
            {
                "heading": s.heading,
                "level": s.level,
                "text": s.text,
                "source": _source_to_dict(s.source),
            }
            for s in m.sections
        ],
        "tables": [
            {
                "title": t.title,
                "columns": t.columns,
                "rows": t.rows,
                "source": _source_to_dict(t.source),
            }
            for t in m.tables
        ],
        "figure_refs": [
            {
                "caption": f.caption,
                "figure_id": f.figure_id,
                "source": _source_to_dict(f.source),
            }
            for f in m.figure_refs
        ],
        "extraction_stats": m.extraction_stats,
        "errors": m.errors,
    }


def manifest_from_dict(d: dict) -> DocumentManifest:
    """Reconstruct a DocumentManifest from a plain dict."""
    meta_d = d["metadata"]
    meta = DocumentMetadata(
        filename=meta_d["filename"],
        format=meta_d["format"],
        size_bytes=meta_d["size_bytes"],
        pages=meta_d.get("pages"),
        sheets=meta_d.get("sheets"),
        checksum=meta_d.get("checksum"),
        extraction_timestamp=meta_d.get("extraction_timestamp"),
    )
    sections = [
        ExtractedSection(
            heading=s["heading"],
            level=s["level"],
            text=s["text"],
            source=_source_from_dict(s["source"]),
        )
        for s in d.get("sections", [])
    ]
    tables = [
        ExtractedTable(
            title=t["title"],
            columns=t["columns"],
            rows=t["rows"],
            source=_source_from_dict(t["source"]),
        )
        for t in d.get("tables", [])
    ]
    figure_refs = [
        ExtractedFigureRef(
            caption=f["caption"],
            figure_id=f["figure_id"],
            source=_source_from_dict(f["source"]),
        )
        for f in d.get("figure_refs", [])
    ]
    return DocumentManifest(
        version=d["version"],
        tool=d["tool"],
        domain=d["domain"],
        metadata=meta,
        doc_ref=d.get("doc_ref"),
        sections=sections,
        tables=tables,
        figure_refs=figure_refs,
        extraction_stats=d.get("extraction_stats", {}),
        errors=d.get("errors", []),
    )


def write_manifest(manifest: DocumentManifest, path: Path) -> None:
    """Atomically write a manifest to YAML."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    d = manifest_to_dict(manifest)
    tmp = path.with_suffix(".yaml.tmp")
    tmp.write_text(yaml.dump(d, default_flow_style=False, sort_keys=False))
    os.replace(tmp, path)
