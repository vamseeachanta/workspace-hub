---
name: pypdf-1-memory-management
description: 'Sub-skill of pypdf: 1. Memory Management (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Memory Management (+2)

## 1. Memory Management


```python
"""Best practices for handling large PDFs."""

# DO: Process pages one at a time for large files
def process_large_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Process page
        writer.add_page(page)
        # Writer streams to file, not memory

    writer.write(output_path)

# DO: Use context managers when available
with open('document.pdf', 'rb') as f:
    reader = PdfReader(f)
    # Process...
```


## 2. Error Handling


```python
"""Robust error handling for PDF operations."""
from pypdf.errors import PdfReadError, PdfReadWarning

def safe_read_pdf(pdf_path):
    """Safely read PDF with error handling."""
    try:
        reader = PdfReader(pdf_path)
        return reader, None
    except PdfReadError as e:
        return None, f"Invalid PDF: {e}"
    except FileNotFoundError:
        return None, f"File not found: {pdf_path}"
    except PermissionError:
        return None, f"Permission denied: {pdf_path}"
    except Exception as e:
        return None, f"Unexpected error: {e}"
```


## 3. Validation


```python
"""Validate PDF files before processing."""

def validate_pdf(pdf_path):
    """Validate PDF file."""
    path = Path(pdf_path)

    if not path.exists():
        return False, "File does not exist"

    if path.suffix.lower() != '.pdf':
        return False, "Not a PDF file"

    try:
        reader = PdfReader(pdf_path)
        _ = len(reader.pages)  # Try to access pages
        return True, "Valid PDF"
    except Exception as e:
        return False, f"Invalid PDF: {e}"
```
