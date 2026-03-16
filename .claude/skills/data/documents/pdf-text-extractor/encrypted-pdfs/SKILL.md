---
name: pdf-text-extractor-encrypted-pdfs
description: 'Sub-skill of pdf-text-extractor: Encrypted PDFs (+2).'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Encrypted PDFs (+2)

## Encrypted PDFs


```python
def extract_with_password(filepath, password=None):
    doc = fitz.open(filepath)

    if doc.is_encrypted:
        if password:
            if not doc.authenticate(password):
                raise ValueError("Invalid password")
        else:
            raise ValueError("PDF is encrypted")

    # Continue extraction...
```

## Scanned PDFs (OCR)


```python
# For scanned PDFs, use OCR
import pytesseract
from PIL import Image

def extract_with_ocr(filepath):
    doc = fitz.open(filepath)
    pages = []

    for page in doc:

*See sub-skills for full details.*

## Large PDFs


```python
def extract_large_pdf(filepath, max_pages=None):
    """Extract with memory-efficient streaming."""
    doc = fitz.open(filepath)

    for page_num, page in enumerate(doc, 1):
        if max_pages and page_num > max_pages:
            break

        text = page.get_text()

*See sub-skills for full details.*
