---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. Use when Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
version: 1.1.0
last_updated: 2026-01-02
category: document-handling
related_skills:
  - pdf-text-extractor
  - document-rag-pipeline
  - knowledge-base-builder
---

# PDF Processing Skill

## Overview

This skill enables comprehensive PDF operations through Python libraries and command-line tools. Use it for reading, creating, modifying, and analyzing PDF documents.

## Quick Start

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for page in reader.pages:
    text = page.extract_text()
    print(text)
```

## When to Use

- Extracting text and metadata from PDF files
- Merging multiple PDFs into a single document
- Splitting large PDFs into individual pages
- Adding watermarks or annotations to PDFs
- Password-protecting or decrypting PDFs
- Extracting images from PDF documents
- OCR processing for scanned documents
- Creating new PDFs with reportlab
- Extracting tables from structured PDFs

## Python Libraries

### pypdf - Core PDF Operations

**Merging PDFs:**
```python
from pypdf import PdfMerger

merger = PdfMerger()
merger.append("file1.pdf")
merger.append("file2.pdf")
merger.write("merged.pdf")
merger.close()
```

**Splitting PDFs:**
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(f"page_{i+1}.pdf")
```

**Extracting Metadata:**
```python
reader = PdfReader("document.pdf")
info = reader.metadata
print(f"Author: {info.author}")
print(f"Title: {info.title}")
print(f"Pages: {len(reader.pages)}")
```

### pdfplumber - Advanced Text Extraction

**Text with Layout Preservation:**
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

**Table Extraction:**
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            print(row)
```

### reportlab - Creating PDFs

**Create PDF from Scratch:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=letter)
c.drawString(100, 750, "Hello, World!")
c.showPage()
c.save()
```

**Multi-page Documents:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("output.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Title", styles['Heading1']))
story.append(Paragraph("Body text here.", styles['Normal']))

doc.build(story)
```

## Command-Line Tools

### pdftotext (Poppler)
```bash
pdftotext document.pdf output.txt
pdftotext -layout document.pdf output.txt  # Preserve layout
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf document.pdf --pages . 1-5 -- first_five.pdf

# Decrypt
qpdf --decrypt encrypted.pdf decrypted.pdf
```

### pdftk
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk document.pdf burst output page_%02d.pdf

# Rotate
pdftk document.pdf cat 1-endeast output rotated.pdf
```

## Common Tasks

### OCR for Scanned Documents
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf")
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
    print(f"Page {i+1}:\n{text}")
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
watermark = PdfReader("watermark.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark.pages[0])
    writer.add_page(page)

writer.write("watermarked.pdf")
```

### Extract Images
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for page_num, page in enumerate(reader.pages):
    for img_num, image in enumerate(page.images):
        with open(f"image_{page_num}_{img_num}.png", "wb") as f:
            f.write(image.data)
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.encrypt("user_password", "owner_password")
writer.write("protected.pdf")
```

## Execution Checklist

- [ ] Verify input PDF exists and is readable
- [ ] Check if PDF is encrypted/DRM-protected
- [ ] Choose appropriate library for task (pypdf vs pdfplumber)
- [ ] Handle multi-page documents correctly
- [ ] Validate output file was created
- [ ] Clean up temporary files

## Error Handling

### Common Errors

**Error: FileNotFoundError**
- Cause: PDF file path is incorrect
- Solution: Verify file path and ensure file exists

**Error: PdfReadError (encrypted)**
- Cause: PDF is password-protected or DRM-encrypted
- Solution: Provide password or use qpdf to decrypt

**Error: Empty text extraction**
- Cause: PDF contains scanned images, not text
- Solution: Use OCR with pytesseract and pdf2image

**Error: DependencyError (Tesseract)**
- Cause: Tesseract OCR not installed
- Solution: `sudo apt-get install tesseract-ocr` or `brew install tesseract`

## Metrics

| Metric | Typical Value |
|--------|---------------|
| Text extraction speed | ~50 pages/second |
| OCR processing speed | ~2-5 pages/minute |
| Memory usage (pypdf) | ~10MB per 100 pages |
| Merge operation | ~100 PDFs/second |

## Quick Reference

| Task | Tool |
|------|------|
| Read text | pypdf, pdfplumber |
| Extract tables | pdfplumber |
| Create PDFs | reportlab |
| Merge/split | pypdf, qpdf, pdftk |
| OCR | pytesseract + pdf2image |
| Fill forms | pypdf, pdfrw |
| Watermark | pypdf |
| Encrypt/decrypt | pypdf, qpdf |

## Dependencies

```bash
pip install pypdf pdfplumber reportlab pytesseract pdf2image
```

System tools:
- Poppler (pdftotext, pdftoppm)
- qpdf
- pdftk
- Tesseract OCR

---

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with pypdf, pdfplumber, reportlab, CLI tools
