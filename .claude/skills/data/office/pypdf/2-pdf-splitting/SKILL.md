---
name: pypdf-2-pdf-splitting
description: 'Sub-skill of pypdf: 2. PDF Splitting.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 2. PDF Splitting

## 2. PDF Splitting


```python
"""
Split PDF files into separate documents.
"""
from pypdf import PdfReader, PdfWriter
from pathlib import Path
from typing import List, Tuple, Optional

def split_pdf_by_pages(
    input_path: str,
    output_dir: str,
    pages_per_file: int = 1
) -> List[str]:
    """Split PDF into multiple files with specified pages per file."""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    input_name = Path(input_path).stem
    created_files = []

    for start in range(0, total_pages, pages_per_file):
        writer = PdfWriter()
        end = min(start + pages_per_file, total_pages)

        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        # Generate output filename
        if pages_per_file == 1:
            output_file = output_path / f"{input_name}_page_{start + 1}.pdf"
        else:
            output_file = output_path / f"{input_name}_pages_{start + 1}-{end}.pdf"

        writer.write(str(output_file))
        created_files.append(str(output_file))

        print(f"Created: {output_file.name}")

    print(f"Split into {len(created_files)} files")
    return created_files


def extract_pages(
    input_path: str,
    output_path: str,
    page_numbers: List[int]
) -> None:
    """Extract specific pages from a PDF.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        page_numbers: List of page numbers (0-indexed)
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page_num in page_numbers:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
            print(f"Extracted page {page_num + 1}")
        else:
            print(f"Warning: Page {page_num + 1} out of range")

    writer.write(output_path)
    print(f"Extracted pages saved to: {output_path}")


def split_by_ranges(
    input_path: str,
    output_dir: str,
    ranges: List[Tuple[int, int, str]]
) -> List[str]:
    """Split PDF by specified page ranges.

    Args:
        input_path: Source PDF file
        output_dir: Output directory
        ranges: List of (start, end, name) tuples
                start and end are 0-indexed
    """
    reader = PdfReader(input_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    created_files = []

    for start, end, name in ranges:
        writer = PdfWriter()

        for page_num in range(start, min(end, len(reader.pages))):
            writer.add_page(reader.pages[page_num])

        output_file = output_path / f"{name}.pdf"
        writer.write(str(output_file))
        created_files.append(str(output_file))

        print(f"Created: {output_file.name} (pages {start + 1}-{end})")

    return created_files


def split_by_bookmarks(
    input_path: str,
    output_dir: str
) -> List[str]:
    """Split PDF by bookmark (outline) entries."""
    reader = PdfReader(input_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not reader.outline:
        print("No bookmarks found in PDF")
        return []

    created_files = []

    # Get bookmark page numbers
    bookmarks = []
    for item in reader.outline:
        if isinstance(item, list):
            continue  # Skip nested bookmarks
        try:
            page_num = reader.get_destination_page_number(item)
            title = item.title
            bookmarks.append((page_num, title))
        except:
            continue

    # Sort by page number
    bookmarks.sort(key=lambda x: x[0])

    # Add end marker
    bookmarks.append((len(reader.pages), "END"))

    # Create PDFs for each section
    for i in range(len(bookmarks) - 1):
        start_page, title = bookmarks[i]
        end_page = bookmarks[i + 1][0]

        if start_page >= end_page:
            continue

        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        # Clean filename
        safe_title = "".join(c if c.isalnum() or c in ' -_' else '_' for c in title)
        output_file = output_path / f"{i + 1:02d}_{safe_title}.pdf"

        writer.write(str(output_file))
        created_files.append(str(output_file))

        print(f"Created: {output_file.name}")

    return created_files


# Example usage
# split_pdf_by_pages('large_document.pdf', 'split_output/', pages_per_file=10)
# extract_pages('document.pdf', 'selected_pages.pdf', [0, 4, 9])  # Pages 1, 5, 10
# split_by_ranges('manual.pdf', 'chapters/', [
#     (0, 10, 'chapter_1'),
#     (10, 25, 'chapter_2'),
#     (25, 40, 'chapter_3')
# ])
```
