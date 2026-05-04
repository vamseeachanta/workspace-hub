---
name: pypdf-4-watermarking-and-stamping
description: 'Sub-skill of pypdf: 4. Watermarking and Stamping.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. Watermarking and Stamping

## 4. Watermarking and Stamping


```python
"""
Add watermarks, stamps, and overlays to PDF pages.
"""
from pypdf import PdfReader, PdfWriter
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

# For creating watermarks
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import Color
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def create_text_watermark(
    text: str,
    output_path: str,
    font_size: int = 60,
    opacity: float = 0.3,
    rotation: int = 45,
    color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
) -> str:
    """Create a watermark PDF with specified text."""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for creating watermarks")

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter

    # Set transparency
    c.setFillColor(Color(*color, alpha=opacity))

    # Save state, rotate, draw text
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(rotation)
    c.setFont("Helvetica-Bold", font_size)

    # Draw text centered
    text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
    c.drawString(-text_width / 2, 0, text)

    c.restoreState()
    c.save()

    # Write to file
    packet.seek(0)
    with open(output_path, 'wb') as f:
        f.write(packet.getvalue())

    return output_path


def add_watermark(
    input_path: str,
    watermark_path: str,
    output_path: str,
    pages: Optional[list] = None
) -> None:
    """Add watermark to PDF pages.

    Args:
        input_path: Source PDF file
        watermark_path: Watermark PDF file
        output_path: Destination file
        pages: List of page numbers to watermark (0-indexed), None for all
    """
    reader = PdfReader(input_path)
    watermark_reader = PdfReader(watermark_path)
    watermark_page = watermark_reader.pages[0]

    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if pages is None or i in pages:
            page.merge_page(watermark_page)
        writer.add_page(page)

    writer.write(output_path)
    print(f"Watermarked PDF saved to: {output_path}")


def add_page_numbers(
    input_path: str,
    output_path: str,
    position: str = "bottom-center",
    start_number: int = 1,
    prefix: str = "Page ",
    font_size: int = 10
) -> None:
    """Add page numbers to PDF.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        position: Position of page number (bottom-center, bottom-right, etc.)
        start_number: Starting page number
        prefix: Text before page number
        font_size: Font size for page numbers
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for adding page numbers")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        # Get page dimensions
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Create page number overlay
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))

        # Calculate position
        page_num_text = f"{prefix}{start_number + i}"

        if position == "bottom-center":
            x = width / 2
            y = 30
        elif position == "bottom-right":
            x = width - 50
            y = 30
        elif position == "top-center":
            x = width / 2
            y = height - 30
        elif position == "top-right":
            x = width - 50
            y = height - 30
        else:
            x = width / 2
            y = 30

        c.setFont("Helvetica", font_size)
        text_width = c.stringWidth(page_num_text, "Helvetica", font_size)

        if "center" in position:
            x -= text_width / 2

        c.drawString(x, y, page_num_text)
        c.save()

        # Merge with page
        packet.seek(0)
        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    writer.write(output_path)
    print(f"Page numbers added to: {output_path}")


def add_header_footer(
    input_path: str,
    output_path: str,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    font_size: int = 10
) -> None:
    """Add header and/or footer to all pages."""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for adding headers/footers")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Create overlay
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        c.setFont("Helvetica", font_size)

        if header:
            text_width = c.stringWidth(header, "Helvetica", font_size)

*Content truncated — see parent skill for full reference.*
