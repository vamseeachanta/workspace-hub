#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
#     "pdfplumber",
#     "pytesseract",
#     "pdf2image",
#     "Pillow",
# ]
# ///
"""OCR parser for scanned PDF extraction (#1617).

Integrates with the existing doc-intelligence extraction pipeline.
Handles three scenarios:
  1. Text PDFs  — delegates to existing PdfParser (pdfplumber)
  2. Scanned PDFs — uses pytesseract + pdf2image for OCR
  3. Mixed PDFs — text pages via pdfplumber, scanned pages via OCR

Requires:
  - tesseract-ocr system package (apt install tesseract-ocr)
  - pdf2image requires poppler-utils (apt install poppler-utils)

If tesseract is not installed, the script returns a manifest with
a clear error message and zero extracted content.

Usage:
    uv run scripts/document_intelligence/ocr_parser.py --input <file.pdf> [--domain <domain>]

API:
    from scripts.document_intelligence.ocr_parser import ocr_extract
    manifest = ocr_extract("path/to/scanned.pdf", domain="engineering")
"""

import argparse
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure repo root on PYTHONPATH
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.data.doc_intelligence.schema import (
    DocumentManifest,
    DocumentMetadata,
    ExtractedFigureRef,
    ExtractedSection,
    ExtractedTable,
    SourceLocation,
)

# ---------------------------------------------------------------------------
# Dependency detection
# ---------------------------------------------------------------------------

_HAS_TESSERACT = shutil.which("tesseract") is not None

try:
    import pdfplumber  # noqa: F401
    _HAS_PDFPLUMBER = True
except ImportError:
    _HAS_PDFPLUMBER = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_checksum(filepath: str) -> str:
    """SHA-256 checksum of the file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _empty_manifest(
    filepath: str, domain: str, errors: List[str]
) -> DocumentManifest:
    """Return a manifest with metadata but no extracted content."""
    p = Path(filepath)
    try:
        size = p.stat().st_size
    except OSError:
        size = 0
    meta = DocumentMetadata(
        filename=p.name,
        format="pdf",
        size_bytes=size,
        checksum=None,
        extraction_timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return DocumentManifest(
        version="1.0.0",
        tool="ocr-parser/1.0.0",
        domain=domain,
        metadata=meta,
        sections=[],
        tables=[],
        figure_refs=[],
        extraction_stats={"sections": 0, "tables": 0, "figure_refs": 0},
        errors=errors,
    )


def _extract_text_per_page(filepath: str) -> Dict[int, str]:
    """Use pdfplumber to extract text per page. Returns {page_num: text}."""
    if not _HAS_PDFPLUMBER:
        return {}
    result: Dict[int, str] = {}
    try:
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                result[i] = text.strip()
    except Exception:
        pass
    return result


def _page_count(filepath: str) -> int:
    """Get total number of pages in the PDF."""
    if not _HAS_PDFPLUMBER:
        return 0
    try:
        with pdfplumber.open(filepath) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# OCR engine
# ---------------------------------------------------------------------------

def _ocr_page_images(filepath: str) -> List[Tuple[int, str]]:
    """Convert PDF pages to images and OCR each one.

    Returns list of (page_number, extracted_text).
    Requires: tesseract-ocr, poppler-utils (for pdf2image).
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as exc:
        raise RuntimeError(
            f"OCR dependencies not available: {exc}. "
            "Install with: apt install tesseract-ocr poppler-utils && "
            "uv pip install pytesseract pdf2image Pillow"
        ) from exc

    images = convert_from_path(filepath, dpi=300)
    results: List[Tuple[int, str]] = []
    for page_num, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img)
        if text.strip():
            results.append((page_num, text.strip()))
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_scanned_pdf(filepath: str, text_threshold: int = 50) -> bool:
    """Detect whether a PDF is scanned (image-only, no extractable text).

    A PDF is considered scanned if pdfplumber extracts fewer than
    `text_threshold` characters of meaningful text across ALL pages.

    Args:
        filepath: Path to the PDF file.
        text_threshold: Minimum total characters to consider "has text".

    Returns:
        True if the PDF appears to be scanned (no/minimal extractable text).
    """
    pages = _extract_text_per_page(filepath)
    total_text = sum(len(t) for t in pages.values())
    return total_text < text_threshold


def ocr_extract(filepath: str, domain: str = "general") -> DocumentManifest:
    """Extract text from a scanned PDF using OCR.

    Falls back gracefully if tesseract is not installed.

    Args:
        filepath: Path to the PDF file.
        domain: Domain label for the manifest.

    Returns:
        DocumentManifest compatible with the doc-intelligence pipeline.
    """
    p = Path(filepath)

    # Guard: file must exist
    if not p.exists():
        return _empty_manifest(filepath, domain, [f"File not found: {filepath}"])

    # Guard: must be PDF
    if p.suffix.lower() != ".pdf":
        return _empty_manifest(
            filepath, domain, [f"Not a PDF file: {p.suffix}"]
        )

    # Validate the PDF can be opened
    try:
        if _HAS_PDFPLUMBER:
            with pdfplumber.open(filepath) as pdf:
                page_count = len(pdf.pages)
        else:
            page_count = None
    except Exception as exc:
        return _empty_manifest(
            filepath, domain,
            [f"PDF extraction failed: {exc}"]
        )

    # Check tesseract availability
    if not _HAS_TESSERACT:
        return _empty_manifest(
            filepath, domain,
            [
                "Tesseract OCR is not installed. Install with: "
                "apt install tesseract-ocr poppler-utils. "
                "Scanned PDF cannot be processed without OCR."
            ],
        )

    # Run OCR
    meta = DocumentMetadata(
        filename=p.name,
        format="pdf",
        size_bytes=p.stat().st_size,
        pages=page_count,
        checksum=_compute_checksum(filepath),
        extraction_timestamp=datetime.now(timezone.utc).isoformat(),
    )
    sections: List[ExtractedSection] = []
    errors: List[str] = []

    try:
        ocr_pages = _ocr_page_images(filepath)
        for page_num, text in ocr_pages:
            sections.append(
                ExtractedSection(
                    heading=None,
                    level=0,
                    text=text,
                    source=SourceLocation(document=p.name, page=page_num),
                )
            )
    except Exception as exc:
        errors.append(f"OCR extraction failed: {exc}")

    return DocumentManifest(
        version="1.0.0",
        tool="ocr-parser/1.0.0",
        domain=domain,
        metadata=meta,
        sections=sections,
        tables=[],
        figure_refs=[],
        extraction_stats={
            "sections": len(sections),
            "tables": 0,
            "figure_refs": 0,
        },
        errors=errors,
    )


def mixed_pdf_extract(
    filepath: str,
    domain: str = "general",
    text_pages: Optional[Dict[int, str]] = None,
    scanned_pages: Optional[List[int]] = None,
) -> DocumentManifest:
    """Extract from a mixed PDF: text pages direct, scanned pages via OCR.

    Args:
        filepath: Path to the PDF file.
        domain: Domain label.
        text_pages: {page_num: text} for pages with extractable text.
                    If None, auto-detects using pdfplumber.
        scanned_pages: List of page numbers that need OCR.
                       If None, auto-detects (pages with <50 chars).

    Returns:
        DocumentManifest with all pages combined.
    """
    p = Path(filepath)
    if not p.exists():
        return _empty_manifest(filepath, domain, [f"File not found: {filepath}"])

    # Auto-detect text vs scanned pages
    if text_pages is None or scanned_pages is None:
        all_pages = _extract_text_per_page(filepath)
        if text_pages is None:
            text_pages = {k: v for k, v in all_pages.items() if len(v) >= 50}
        if scanned_pages is None:
            scanned_pages = [k for k, v in all_pages.items() if len(v) < 50]

    meta = DocumentMetadata(
        filename=p.name,
        format="pdf",
        size_bytes=p.stat().st_size,
        pages=_page_count(filepath) or None,
        checksum=_compute_checksum(filepath),
        extraction_timestamp=datetime.now(timezone.utc).isoformat(),
    )

    sections: List[ExtractedSection] = []
    errors: List[str] = []

    # Direct-extracted text pages
    for page_num in sorted(text_pages.keys()):
        text = text_pages[page_num]
        if text.strip():
            sections.append(
                ExtractedSection(
                    heading=None,
                    level=0,
                    text=text.strip(),
                    source=SourceLocation(document=p.name, page=page_num),
                )
            )

    # OCR scanned pages
    if scanned_pages and _HAS_TESSERACT:
        try:
            ocr_results = _ocr_page_images(filepath)
            ocr_map = {pn: txt for pn, txt in ocr_results}
            for page_num in sorted(scanned_pages):
                text = ocr_map.get(page_num, "")
                if text.strip():
                    sections.append(
                        ExtractedSection(
                            heading=None,
                            level=0,
                            text=text.strip(),
                            source=SourceLocation(
                                document=p.name, page=page_num
                            ),
                        )
                    )
        except Exception as exc:
            errors.append(f"OCR failed for scanned pages: {exc}")
    elif scanned_pages and not _HAS_TESSERACT:
        errors.append(
            f"Tesseract not installed — {len(scanned_pages)} scanned page(s) "
            "could not be OCR'd. Install: apt install tesseract-ocr"
        )

    return DocumentManifest(
        version="1.0.0",
        tool="ocr-parser/1.0.0",
        domain=domain,
        metadata=meta,
        sections=sections,
        tables=[],
        figure_refs=[],
        extraction_stats={
            "sections": len(sections),
            "tables": 0,
            "figure_refs": 0,
        },
        errors=errors,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OCR parser for scanned PDF extraction (#1617)"
    )
    parser.add_argument("--input", required=True, help="Path to input PDF")
    parser.add_argument(
        "--domain", default="general", help="Domain label (default: general)"
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    filepath = Path(args.input)
    if not filepath.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1

    scanned = is_scanned_pdf(str(filepath))
    if args.verbose:
        print(f"Scanned PDF detected: {scanned}")

    if scanned:
        manifest = ocr_extract(str(filepath), domain=args.domain)
    else:
        # Mixed/text — try mixed extraction
        manifest = mixed_pdf_extract(str(filepath), domain=args.domain)

    if manifest.errors:
        for err in manifest.errors:
            print(f"  Warning: {err}", file=sys.stderr)

    stats = manifest.extraction_stats
    print(
        f"Extracted: {stats.get('sections', 0)} sections, "
        f"{stats.get('tables', 0)} tables"
    )
    return 0 if not manifest.errors or manifest.sections else 1


if __name__ == "__main__":
    sys.exit(main())
