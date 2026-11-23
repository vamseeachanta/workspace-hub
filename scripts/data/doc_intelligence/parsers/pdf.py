"""PDF parser using pdfplumber for text and table extraction.

Falls back to pdftotext (poppler) when pdfplumber produces CID-corrupted text
(embedded font glyph IDs that can't be mapped to Unicode). pypdfium2 was tested
but also fails on these PDFs; pdftotext handles them correctly.
"""

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List

try:
    import pdfplumber
except ModuleNotFoundError:  # optional dependency during collection
    pdfplumber = None

from scripts.data.doc_intelligence.parsers.base import BaseParser
from scripts.data.doc_intelligence.schema import (
    DocumentManifest,
    DocumentMetadata,
    ExtractedFigureRef,
    ExtractedSection,
    ExtractedTable,
    SourceLocation,
)

FIGURE_RE = re.compile(
    r"(Figure\s+\d+[\.\d]*)\s*[:\.\-\u2014]?\s*(.*)",
    re.IGNORECASE,
)

_CID_PATTERN = re.compile(r"\(cid:\d+\)")


def _has_cid_corruption(text: str, threshold: float = 0.10) -> bool:
    """Return True if CID character codes exceed threshold fraction of text."""
    if not text or len(text) < 50:
        return False
    cid_chars = sum(len(m.group()) for m in _CID_PATTERN.finditer(text))
    return (cid_chars / len(text)) > threshold


def _extract_pages_pdftotext(filepath: str) -> list[tuple[int, str]]:
    """Extract per-page text using pdftotext (poppler) as fallback for CID-corrupted PDFs.

    pdftotext handles embedded font encoding that pdfplumber and pypdfium2 cannot resolve.
    Extracts all pages in a single subprocess call, splits on form-feed characters.
    Returns list of (page_number, text) tuples. Empty list if pdftotext unavailable.
    """
    import shutil
    import subprocess

    if not shutil.which("pdftotext"):
        return []

    try:
        result = subprocess.run(
            ["pdftotext", "-q", filepath, "-"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return []
    except Exception:
        return []

    # pdftotext separates pages with form-feed (\f) characters
    raw_pages = result.stdout.split("\f")
    pages = []
    for i, text in enumerate(raw_pages):
        if text.strip():  # skip trailing empty page after last \f
            pages.append((i + 1, text))
    return pages


def _compute_checksum(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _extract_figure_refs(
    text: str, document: str, page: int
) -> List[ExtractedFigureRef]:
    refs = []
    for match in FIGURE_RE.finditer(text):
        refs.append(
            ExtractedFigureRef(
                caption=match.group(2).strip() or None,
                figure_id=match.group(1).strip(),
                source=SourceLocation(document=document, page=page),
            )
        )
    return refs


class PdfParser(BaseParser):
    """Extract sections, tables, and figure references from PDF files."""

    def can_handle(self, filepath: str) -> bool:
        return Path(filepath).suffix.lower() == ".pdf"

    def parse(self, filepath: str, domain: str) -> DocumentManifest:
        p = Path(filepath)
        meta = DocumentMetadata(
            filename=p.name,
            format="pdf",
            size_bytes=p.stat().st_size,
            checksum=_compute_checksum(filepath),
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        sections: List[ExtractedSection] = []
        tables: List[ExtractedTable] = []
        figure_refs: List[ExtractedFigureRef] = []
        errors: List[str] = []

        if pdfplumber is None:
            errors.append("pdfplumber is not installed")
            return DocumentManifest(version="1.0.0", tool="extract-document/1.0.0", domain=domain, metadata=meta, sections=sections, tables=tables, figure_refs=figure_refs, errors=errors)

        try:
            with pdfplumber.open(filepath) as pdf:
                meta.pages = len(pdf.pages)

                # Phase 1: Try pdfplumber, detect CID corruption on first 5 pages
                sample_text = ""
                for page in pdf.pages[:5]:
                    sample_text += (page.extract_text() or "") + "\n"

                use_fallback = _has_cid_corruption(sample_text)
                if use_fallback:
                    errors.append(
                        "CID corruption detected in pdfplumber output; "
                        "falling back to pdftotext (poppler)"
                    )

                # Phase 2: Extract text (pypdfium2 fallback or pdfplumber)
                if use_fallback:
                    fallback_pages = _extract_pages_pdftotext(filepath)
                    for page_num, text in fallback_pages:
                        src = SourceLocation(document=p.name, page=page_num)
                        if text.strip():
                            sections.append(
                                ExtractedSection(
                                    heading=None,
                                    level=0,
                                    text=text.strip(),
                                    source=src,
                                )
                            )
                            figure_refs.extend(
                                _extract_figure_refs(text, p.name, page_num)
                            )
                else:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        src = SourceLocation(document=p.name, page=page_num)
                        text = page.extract_text() or ""
                        if text.strip():
                            sections.append(
                                ExtractedSection(
                                    heading=None,
                                    level=0,
                                    text=text.strip(),
                                    source=src,
                                )
                            )
                            figure_refs.extend(
                                _extract_figure_refs(text, p.name, page_num)
                            )

                # Tables always via pdfplumber (pypdfium2 doesn't extract tables)
                for page_num, page in enumerate(pdf.pages, start=1):
                    src = SourceLocation(document=p.name, page=page_num)
                    for tbl in page.extract_tables() or []:
                        if not tbl or len(tbl) < 2:
                            continue
                        header = [str(c) if c else "" for c in tbl[0]]
                        rows = [
                            [str(c) if c else "" for c in row]
                            for row in tbl[1:]
                        ]
                        tables.append(
                            ExtractedTable(
                                title=None,
                                columns=header,
                                rows=rows,
                                source=src,
                            )
                        )
        except Exception as exc:
            errors.append(f"PDF extraction failed: {exc}")

        return DocumentManifest(
            version="1.0.0",
            tool="extract-document/1.0.0",
            domain=domain,
            metadata=meta,
            sections=sections,
            tables=tables,
            figure_refs=figure_refs,
            extraction_stats={
                "sections": len(sections),
                "tables": len(tables),
                "figure_refs": len(figure_refs),
            },
            errors=errors,
        )
