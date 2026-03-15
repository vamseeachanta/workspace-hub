"""Chart extractor — extracts images from PDFs and generates calibration metadata.

Uses PyMuPDF (fitz) to extract embedded images from PDF pages during a single
parse pass. Links extracted images to figure references from the manifest.
Generates calibration metadata YAML for manual digitization.

Usage:
    from scripts.data.doc_intelligence.chart_extractor import (
        extract_images_from_pdf, generate_chart_metadata,
    )
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Minimum dimensions to consider an image a chart (filters icons/logos/rules)
MIN_WIDTH = 100
MIN_HEIGHT = 80


@dataclass
class ChartImage:
    """An image extracted from a PDF."""

    image_hash: str
    page: int
    index: int  # image index within page
    width: int
    height: int
    format: str  # png, jpeg, etc.

    @property
    def filename(self) -> str:
        return f"{self.image_hash}.{self.format}"


def _is_chart_candidate(width: int, height: int) -> bool:
    """Check if image dimensions suggest a chart/figure vs icon/logo."""
    return width >= MIN_WIDTH and height >= MIN_HEIGHT


def extract_images_from_pdf(
    pdf_path: Path,
    output_dir: Path,
    min_width: int = MIN_WIDTH,
    min_height: int = MIN_HEIGHT,
) -> list[ChartImage]:
    """Extract images from a PDF using PyMuPDF.

    Saves each qualifying image to output_dir/{sha256}.{ext}.
    Returns list of ChartImage objects describing extracted images.
    Skips small images (icons, logos, horizontal rules).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        return []

    try:
        import fitz
    except ImportError:
        return []

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    images: list[ChartImage] = []

    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return []

    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            for img_idx, img_info in enumerate(image_list):
                xref = img_info[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                except Exception:
                    continue

                width = pix.width
                height = pix.height

                if not _is_chart_candidate(width, height):
                    pix = None
                    continue

                # Convert CMYK to RGB if needed
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # Determine format
                img_format = "png"
                img_bytes = pix.tobytes(img_format)

                # Hash for deduplication and naming
                img_hash = hashlib.sha256(img_bytes).hexdigest()[:16]

                out_path = output_dir / f"{img_hash}.{img_format}"
                if not out_path.exists():
                    out_path.write_bytes(img_bytes)

                images.append(ChartImage(
                    image_hash=img_hash,
                    page=page_num + 1,  # 1-indexed
                    index=img_idx,
                    width=width,
                    height=height,
                    format=img_format,
                ))
                pix = None
    finally:
        doc.close()

    return images


def generate_chart_metadata(
    figure_refs: list[dict],
    images: list[ChartImage],
    doc_name: str,
    domain: str,
) -> list[dict]:
    """Generate calibration metadata linking figure references to extracted images.

    Matches images to figure refs by page number. Unmatched images get
    standalone entries. All entries include a calibration stub for
    manual digitization tracking.

    Returns list of metadata dicts suitable for YAML serialization.
    """
    if not figure_refs and not images:
        return []

    # Index images by page for matching
    images_by_page: dict[int, list[ChartImage]] = {}
    matched_images: set[str] = set()
    for img in images:
        images_by_page.setdefault(img.page, []).append(img)

    metadata = []

    # Process figure references, linking to images where possible
    for ref in figure_refs:
        page = ref.get("source", {}).get("page")
        entry: dict = {
            "figure_id": ref.get("figure_id"),
            "caption": ref.get("caption"),
            "source": ref.get("source", {}),
            "domain": domain,
            "doc_name": doc_name,
            "digitized": False,
            "image_file": None,
            "image_size": None,
            "calibration": {
                "status": "pending",
                "x_axis": None,
                "y_axis": None,
                "data_points": [],
            },
        }

        # Try to match an image on the same page
        if page and page in images_by_page:
            page_images = images_by_page[page]
            for img in page_images:
                if img.image_hash not in matched_images:
                    entry["image_file"] = img.filename
                    entry["image_size"] = {
                        "width": img.width,
                        "height": img.height,
                    }
                    matched_images.add(img.image_hash)
                    break

        metadata.append(entry)

    # Add orphaned images (no matching figure reference)
    for img in images:
        if img.image_hash not in matched_images:
            metadata.append({
                "figure_id": None,
                "caption": None,
                "source": {"document": doc_name, "page": img.page},
                "domain": domain,
                "doc_name": doc_name,
                "digitized": False,
                "image_file": img.filename,
                "image_size": {"width": img.width, "height": img.height},
                "calibration": {
                    "status": "pending",
                    "x_axis": None,
                    "y_axis": None,
                    "data_points": [],
                },
            })

    return metadata
