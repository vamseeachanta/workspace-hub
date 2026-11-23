---
name: pypdf-5-text-extraction-and-metadata
description: 'Sub-skill of pypdf: 5. Text Extraction and Metadata.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. Text Extraction and Metadata

## 5. Text Extraction and Metadata


```python
"""
Extract text and manage PDF metadata.
"""
from pypdf import PdfReader, PdfWriter
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

def extract_text(
    input_path: str,
    pages: Optional[List[int]] = None,
    preserve_layout: bool = False
) -> str:
    """Extract text from PDF.

    Args:
        input_path: Source PDF file
        pages: List of page numbers to extract (0-indexed), None for all
        preserve_layout: Try to preserve text layout

    Returns:
        Extracted text as string
    """
    reader = PdfReader(input_path)
    text_parts = []

    target_pages = pages if pages else range(len(reader.pages))

    for page_num in target_pages:
        if 0 <= page_num < len(reader.pages):
            page = reader.pages[page_num]

            if preserve_layout:
                page_text = page.extract_text(extraction_mode="layout")
            else:
                page_text = page.extract_text()

            if page_text:
                text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")

    return "\n\n".join(text_parts)


def extract_text_to_file(
    input_path: str,
    output_path: str,
    pages: Optional[List[int]] = None
) -> int:
    """Extract text from PDF and save to file."""
    text = extract_text(input_path, pages)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    word_count = len(text.split())
    print(f"Extracted {word_count} words to: {output_path}")
    return word_count


def get_pdf_info(input_path: str) -> Dict:
    """Get PDF document information and metadata."""
    reader = PdfReader(input_path)

    info = {
        'file_path': input_path,
        'num_pages': len(reader.pages),
        'is_encrypted': reader.is_encrypted,
        'metadata': {}
    }

    # Get metadata
    if reader.metadata:
        metadata = reader.metadata
        info['metadata'] = {
            'title': metadata.get('/Title', ''),
            'author': metadata.get('/Author', ''),
            'subject': metadata.get('/Subject', ''),
            'creator': metadata.get('/Creator', ''),
            'producer': metadata.get('/Producer', ''),
            'creation_date': str(metadata.get('/CreationDate', '')),
            'modification_date': str(metadata.get('/ModDate', ''))
        }

    # Get page dimensions of first page
    if reader.pages:
        first_page = reader.pages[0]
        info['page_width'] = float(first_page.mediabox.width)
        info['page_height'] = float(first_page.mediabox.height)
        info['page_size_inches'] = (
            info['page_width'] / 72,
            info['page_height'] / 72
        )

    return info


def set_pdf_metadata(
    input_path: str,
    output_path: str,
    metadata: Dict[str, str]
) -> None:
    """Set PDF metadata.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        metadata: Dictionary with keys: title, author, subject, keywords, creator
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Copy pages
    for page in reader.pages:
        writer.add_page(page)

    # Set metadata
    writer.add_metadata({
        '/Title': metadata.get('title', ''),
        '/Author': metadata.get('author', ''),
        '/Subject': metadata.get('subject', ''),
        '/Keywords': metadata.get('keywords', ''),
        '/Creator': metadata.get('creator', 'pypdf'),
        '/Producer': 'pypdf',
        '/ModDate': datetime.now().strftime("D:%Y%m%d%H%M%S")
    })

    writer.write(output_path)
    print(f"Metadata updated: {output_path}")


def search_pdf(
    input_path: str,
    search_term: str,
    case_sensitive: bool = False
) -> List[Dict]:
    """Search for text in PDF and return page numbers and context."""
    reader = PdfReader(input_path)
    results = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue

        search_text = text if case_sensitive else text.lower()
        term = search_term if case_sensitive else search_term.lower()

        if term in search_text:
            # Find context around match
            idx = search_text.find(term)
            start = max(0, idx - 50)
            end = min(len(text), idx + len(term) + 50)
            context = text[start:end].replace('\n', ' ')

            results.append({
                'page': i + 1,
                'context': f"...{context}..."
            })

    return results


# Example usage
# text = extract_text('document.pdf')
# info = get_pdf_info('document.pdf')
# set_pdf_metadata('document.pdf', 'with_metadata.pdf', {
#     'title': 'My Document',
#     'author': 'John Doe',
#     'subject': 'Report'
# })
# results = search_pdf('document.pdf', 'important')
```
