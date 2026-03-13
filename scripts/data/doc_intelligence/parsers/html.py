"""HTML parser using BeautifulSoup for text and table extraction."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

from scripts.data.doc_intelligence.parsers.base import BaseParser
from scripts.data.doc_intelligence.schema import (
    DocumentManifest,
    DocumentMetadata,
    ExtractedSection,
    ExtractedTable,
    SourceLocation,
)

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def _compute_checksum(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()


class HtmlParser(BaseParser):
    """Extract sections, tables from HTML files."""

    def can_handle(self, filepath: str) -> bool:
        return Path(filepath).suffix.lower() in (".html", ".htm")

    def parse(
        self,
        filepath: str,
        domain: str,
        source_url: str | None = None,
    ) -> DocumentManifest:
        p = Path(filepath)
        doc_label = source_url or p.name
        meta = DocumentMetadata(
            filename=p.name,
            format="html",
            size_bytes=p.stat().st_size,
            checksum=_compute_checksum(filepath),
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        html_bytes = p.read_bytes()
        soup = BeautifulSoup(html_bytes, "html.parser")

        sections: List[ExtractedSection] = []
        tables: List[ExtractedTable] = []
        errors: List[str] = []
        src = SourceLocation(document=doc_label)

        # Extract headings
        for tag in soup.find_all(HEADING_TAGS):
            text = tag.get_text(strip=True)
            if text:
                level = int(tag.name[1])
                sections.append(
                    ExtractedSection(
                        heading=text, level=level, text=text, source=src
                    )
                )

        # Extract paragraphs and divs (body text)
        for tag in soup.find_all(["p", "div"]):
            text = tag.get_text(strip=True)
            if text:
                sections.append(
                    ExtractedSection(
                        heading=None, level=0, text=text, source=src
                    )
                )

        # Extract tables
        for table_tag in soup.find_all("table"):
            rows_raw = table_tag.find_all("tr")
            if len(rows_raw) < 2:
                continue
            # First row = columns
            columns = [
                cell.get_text(strip=True) for cell in rows_raw[0].find_all(["th", "td"])
            ]
            rows = []
            for tr in rows_raw[1:]:
                row = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
                rows.append(row)
            tables.append(
                ExtractedTable(title=None, columns=columns, rows=rows, source=src)
            )

        return DocumentManifest(
            version="1.0.0",
            tool="extract-url/1.0.0",
            domain=domain,
            metadata=meta,
            sections=sections,
            tables=tables,
            figure_refs=[],
            extraction_stats={
                "sections": len(sections),
                "tables": len(tables),
                "figure_refs": 0,
            },
            errors=errors,
        )
