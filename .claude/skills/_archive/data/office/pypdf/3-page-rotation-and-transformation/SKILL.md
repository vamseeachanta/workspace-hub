---
name: pypdf-3-page-rotation-and-transformation
description: 'Sub-skill of pypdf: 3. Page Rotation and Transformation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. Page Rotation and Transformation

## 3. Page Rotation and Transformation


```python
"""
Rotate, crop, and transform PDF pages.
"""
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from pathlib import Path
from typing import List, Optional

def rotate_pages(
    input_path: str,
    output_path: str,
    rotation: int,
    pages: Optional[List[int]] = None
) -> None:
    """Rotate PDF pages by specified degrees.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        rotation: Rotation in degrees (90, 180, or 270)
        pages: List of page numbers to rotate (0-indexed), None for all
    """
    if rotation not in [90, 180, 270]:
        raise ValueError("Rotation must be 90, 180, or 270 degrees")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if pages is None or i in pages:
            page.rotate(rotation)
        writer.add_page(page)

    writer.write(output_path)
    print(f"Rotated PDF saved to: {output_path}")


def rotate_landscape_pages(
    input_path: str,
    output_path: str
) -> int:
    """Automatically rotate landscape pages to portrait."""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    rotated_count = 0

    for page in reader.pages:
        # Get page dimensions
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Rotate if landscape
        if width > height:
            page.rotate(90)
            rotated_count += 1

        writer.add_page(page)

    writer.write(output_path)
    print(f"Rotated {rotated_count} landscape pages")
    return rotated_count


def crop_pages(
    input_path: str,
    output_path: str,
    crop_box: tuple,
    pages: Optional[List[int]] = None
) -> None:
    """Crop PDF pages to specified dimensions.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        crop_box: (left, bottom, right, top) in points (72 points = 1 inch)
        pages: List of page numbers to crop (0-indexed), None for all
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    left, bottom, right, top = crop_box

    for i, page in enumerate(reader.pages):
        if pages is None or i in pages:
            page.mediabox = RectangleObject([left, bottom, right, top])
            page.cropbox = RectangleObject([left, bottom, right, top])

        writer.add_page(page)

    writer.write(output_path)
    print(f"Cropped PDF saved to: {output_path}")


def scale_pages(
    input_path: str,
    output_path: str,
    scale_x: float = 1.0,
    scale_y: float = 1.0
) -> None:
    """Scale PDF pages by specified factors."""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Apply transformation
        op = Transformation().scale(sx=scale_x, sy=scale_y)
        page.add_transformation(op)

        # Update media box
        page.mediabox.lower_left = (
            float(page.mediabox.lower_left[0]) * scale_x,
            float(page.mediabox.lower_left[1]) * scale_y
        )
        page.mediabox.upper_right = (
            float(page.mediabox.upper_right[0]) * scale_x,
            float(page.mediabox.upper_right[1]) * scale_y
        )

        writer.add_page(page)

    writer.write(output_path)
    print(f"Scaled PDF saved to: {output_path}")


def reorder_pages(
    input_path: str,
    output_path: str,
    new_order: List[int]
) -> None:
    """Reorder PDF pages according to specified order.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        new_order: List of page indices in desired order (0-indexed)
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page_num in new_order:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])

    writer.write(output_path)
    print(f"Reordered PDF saved to: {output_path}")


# Example usage
# rotate_pages('document.pdf', 'rotated.pdf', 90)
# rotate_pages('document.pdf', 'rotated.pdf', 90, pages=[0, 2, 4])
# crop_pages('document.pdf', 'cropped.pdf', (72, 72, 540, 720))  # 1 inch margins
# reorder_pages('document.pdf', 'reordered.pdf', [2, 0, 1, 4, 3])
```
