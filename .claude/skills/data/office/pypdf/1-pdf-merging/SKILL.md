---
name: pypdf-1-pdf-merging
description: 'Sub-skill of pypdf: 1. PDF Merging.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. PDF Merging

## 1. PDF Merging


```python
"""
Merge multiple PDF files into a single document.
"""
from pypdf import PdfMerger, PdfReader, PdfWriter
from pathlib import Path
from typing import List, Optional

def merge_pdfs(
    pdf_paths: List[str],
    output_path: str,
    bookmarks: bool = True
) -> None:
    """Merge multiple PDFs into one file."""
    merger = PdfMerger()

    for pdf_path in pdf_paths:
        path = Path(pdf_path)
        if path.exists():
            # Add with bookmark (outline entry)
            merger.append(
                str(pdf_path),
                outline_item=path.stem if bookmarks else None
            )
            print(f"Added: {path.name}")
        else:
            print(f"Warning: File not found - {pdf_path}")

    merger.write(output_path)
    merger.close()

    print(f"Merged PDF saved to: {output_path}")


def merge_with_page_selection(
    pdf_configs: List[dict],
    output_path: str
) -> None:
    """Merge specific pages from multiple PDFs.

    Args:
        pdf_configs: List of dicts with 'path', 'pages' (optional) keys
                    pages can be tuple (start, end) or list of page numbers
        output_path: Output file path
    """
    merger = PdfMerger()

    for config in pdf_configs:
        pdf_path = config['path']
        pages = config.get('pages')

        if pages is None:
            # Add all pages
            merger.append(pdf_path)
        elif isinstance(pages, tuple):
            # Add page range (start, end)
            merger.append(pdf_path, pages=pages)
        elif isinstance(pages, list):
            # Add specific pages
            reader = PdfReader(pdf_path)
            for page_num in pages:
                if 0 <= page_num < len(reader.pages):
                    merger.append(pdf_path, pages=(page_num, page_num + 1))

        print(f"Added: {pdf_path} - Pages: {pages or 'all'}")

    merger.write(output_path)
    merger.close()

    print(f"Merged PDF saved to: {output_path}")


def merge_directory(
    directory: str,
    output_path: str,
    pattern: str = "*.pdf",
    sort_key: Optional[str] = "name"
) -> int:
    """Merge all PDFs in a directory."""
    dir_path = Path(directory)
    pdf_files = list(dir_path.glob(pattern))

    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return 0

    # Sort files
    if sort_key == "name":
        pdf_files.sort(key=lambda x: x.name.lower())
    elif sort_key == "date":
        pdf_files.sort(key=lambda x: x.stat().st_mtime)
    elif sort_key == "size":
        pdf_files.sort(key=lambda x: x.stat().st_size)

    merge_pdfs([str(f) for f in pdf_files], output_path)

    return len(pdf_files)


# Example usage
# merge_pdfs(['report1.pdf', 'report2.pdf', 'appendix.pdf'], 'complete_report.pdf')
#
# merge_with_page_selection([
#     {'path': 'doc1.pdf', 'pages': (0, 5)},  # First 5 pages
#     {'path': 'doc2.pdf', 'pages': [0, 2, 4]},  # Pages 1, 3, 5
#     {'path': 'doc3.pdf'}  # All pages
# ], 'combined.pdf')
```
