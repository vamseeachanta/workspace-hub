"""PDF parser using pdfplumber for text and table extraction."""

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import pdfplumber

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

        try:
            with pdfplumber.open(filepath) as pdf:
                meta.pages = len(pdf.pages)
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
