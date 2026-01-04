---
name: pdf
description: Comprehensive PDF manipulation toolkit with OpenAI Codex integration for intelligent PDF-to-Markdown conversion. IMPORTANT - Always convert PDFs to markdown first using Codex, then process the markdown. Also supports text/table extraction, PDF creation, merging/splitting, and forms. Use for all PDF document processing workflows.
version: 1.2.0
last_updated: 2026-01-04
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

- **Converting PDFs to Markdown** - Use OpenAI Codex for intelligent conversion (RECOMMENDED FIRST STEP)
- Extracting text and metadata from PDF files
- Merging multiple PDFs into a single document
- Splitting large PDFs into individual pages
- Adding watermarks or annotations to PDFs
- Password-protecting or decrypting PDFs
- Extracting images from PDF documents
- OCR processing for scanned documents
- Creating new PDFs with reportlab
- Extracting tables from structured PDFs

## PDF to Markdown Conversion (OpenAI Codex)

**IMPORTANT: For all PDF documents, utilize OpenAI Codex to convert contents to .md file first, then use the markdown for further work.**

### Why Convert to Markdown First?

- **Better structure preservation** - Maintains headings, lists, tables
- **Easier text processing** - Standard markdown format
- **Improved AI understanding** - Codex understands document structure
- **Format flexibility** - Markdown can be converted to any format
- **Version control friendly** - Plain text, diff-friendly

### OpenAI Codex Conversion

**Prerequisites:**
```bash
pip install openai pypdf
export OPENAI_API_KEY="your-api-key-here"
```

**Basic Conversion:**
```python
import openai
from pypdf import PdfReader
from pathlib import Path

def pdf_to_markdown_codex(pdf_path, output_md_path=None, model="gpt-4"):
    """
    Convert PDF to markdown using OpenAI Codex.

    Args:
        pdf_path: Path to PDF file
        output_md_path: Optional path for output .md file (auto-generated if None)
        model: OpenAI model to use (gpt-4, gpt-3.5-turbo, etc.)

    Returns:
        Path to generated markdown file
    """
    # Extract text from PDF
    reader = PdfReader(pdf_path)
    pdf_text = ""

    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        pdf_text += f"\n\n--- Page {page_num} ---\n\n{text}"

    # Generate markdown using OpenAI Codex
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are an expert document converter. Convert the provided PDF text
                to well-structured markdown format. Preserve:
                - Document structure (headings, sections)
                - Lists and bullet points
                - Tables (convert to markdown tables)
                - Code blocks and technical content
                - Links and references

                Format the output as clean, readable markdown."""
            },
            {
                "role": "user",
                "content": f"Convert this PDF text to markdown:\n\n{pdf_text}"
            }
        ],
        temperature=0.3,  # Lower temperature for more consistent formatting
    )

    markdown_content = response.choices[0].message.content

    # Save to file
    if output_md_path is None:
        pdf_stem = Path(pdf_path).stem
        output_md_path = Path(pdf_path).parent / f"{pdf_stem}.md"

    Path(output_md_path).write_text(markdown_content, encoding='utf-8')

    return output_md_path

# Usage
md_file = pdf_to_markdown_codex("document.pdf")
print(f"Markdown saved to: {md_file}")
```

**Batch Conversion:**
```python
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_pdf_to_markdown(pdf_directory, output_directory=None, model="gpt-4"):
    """
    Convert all PDFs in a directory to markdown.

    Args:
        pdf_directory: Directory containing PDF files
        output_directory: Optional output directory (defaults to pdf_directory/markdown)
        model: OpenAI model to use
    """
    pdf_dir = Path(pdf_directory)

    if output_directory is None:
        output_dir = pdf_dir / "markdown"
    else:
        output_dir = Path(output_directory)

    output_dir.mkdir(exist_ok=True)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    total = len(pdf_files)

    logger.info(f"Found {total} PDF files to convert")

    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            output_md = output_dir / f"{pdf_file.stem}.md"

            logger.info(f"[{i}/{total}] Converting {pdf_file.name}...")
            pdf_to_markdown_codex(pdf_file, output_md, model=model)
            logger.info(f"✓ Saved to {output_md.name}")

        except Exception as e:
            logger.error(f"✗ Failed to convert {pdf_file.name}: {e}")

    logger.info(f"\nConversion complete! Files in: {output_dir}")

# Usage
batch_pdf_to_markdown("/path/to/pdfs", model="gpt-4")
```

**Chunked Conversion for Large PDFs:**
```python
def pdf_to_markdown_chunked(pdf_path, output_md_path=None,
                            chunk_pages=10, model="gpt-4"):
    """
    Convert large PDF by processing in chunks.

    Args:
        pdf_path: Path to PDF file
        output_md_path: Optional output path
        chunk_pages: Number of pages per chunk
        model: OpenAI model to use
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    markdown_sections = []

    for start_page in range(0, total_pages, chunk_pages):
        end_page = min(start_page + chunk_pages, total_pages)

        # Extract chunk
        chunk_text = ""
        for page_num in range(start_page, end_page):
            text = reader.pages[page_num].extract_text()
            chunk_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"

        # Convert chunk
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Convert PDF text to markdown. Maintain structure and formatting."
                },
                {
                    "role": "user",
                    "content": f"Convert pages {start_page + 1}-{end_page} to markdown:\n\n{chunk_text}"
                }
            ],
            temperature=0.3,
        )

        markdown_sections.append(response.choices[0].message.content)
        print(f"Processed pages {start_page + 1}-{end_page}/{total_pages}")

    # Combine sections
    full_markdown = "\n\n---\n\n".join(markdown_sections)

    # Save
    if output_md_path is None:
        output_md_path = Path(pdf_path).with_suffix('.md')

    Path(output_md_path).write_text(full_markdown, encoding='utf-8')

    return output_md_path

# Usage
md_file = pdf_to_markdown_chunked("large_document.pdf", chunk_pages=20)
```

**Workflow: PDF → Markdown → Further Processing:**
```python
from pathlib import Path

def pdf_workflow(pdf_path):
    """
    Complete workflow: PDF → Markdown → Process markdown.

    Returns:
        dict with paths to original PDF, markdown, and processed content
    """
    # Step 1: Convert PDF to markdown using Codex
    print("Step 1: Converting PDF to markdown...")
    md_path = pdf_to_markdown_codex(pdf_path)

    # Step 2: Read markdown for further processing
    print("Step 2: Reading markdown content...")
    markdown_content = Path(md_path).read_text(encoding='utf-8')

    # Step 3: Further processing (example: extract headings)
    print("Step 3: Processing markdown...")
    headings = [line for line in markdown_content.split('\n') if line.startswith('#')]

    # Step 4: Additional analysis
    word_count = len(markdown_content.split())

    return {
        'pdf_path': pdf_path,
        'markdown_path': md_path,
        'markdown_content': markdown_content,
        'headings': headings,
        'word_count': word_count,
    }

# Usage
result = pdf_workflow("technical_document.pdf")
print(f"Markdown saved: {result['markdown_path']}")
print(f"Found {len(result['headings'])} headings")
print(f"Word count: {result['word_count']}")

# Now work with the markdown
with open(result['markdown_path']) as f:
    markdown = f.read()
    # Do further processing with clean markdown
```

**Cost-Effective Options:**

```python
# Use GPT-3.5 for cost savings
md_file = pdf_to_markdown_codex("document.pdf", model="gpt-3.5-turbo")

# Or use local extraction + Codex for formatting only
from pypdf import PdfReader

def hybrid_conversion(pdf_path):
    """Extract text locally, use Codex only for formatting."""
    # Extract text (free)
    reader = PdfReader(pdf_path)
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text()

    # Use Codex just for markdown formatting (lower cost)
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Format the text as markdown. Add appropriate headings, lists, and structure."
            },
            {
                "role": "user",
                "content": raw_text
            }
        ],
        temperature=0.3,
    )

    markdown = response.choices[0].message.content
    output_path = Path(pdf_path).with_suffix('.md')
    output_path.write_text(markdown, encoding='utf-8')

    return output_path
```

**Best Practices:**

1. **Always convert to markdown first** - Makes downstream processing easier
2. **Use chunking for large PDFs** - Avoids token limits and API timeouts
3. **Cache conversions** - Store markdown files to avoid re-conversion
4. **Choose model based on complexity** - GPT-4 for complex docs, GPT-3.5 for simple ones
5. **Validate output** - Check that markdown structure makes sense
6. **Handle errors gracefully** - Log failures, continue batch processing

**CLI Tool:**
```bash
#!/usr/bin/env python3
"""PDF to Markdown converter using OpenAI Codex."""

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown using OpenAI')
    parser.add_argument('input', help='PDF file or directory')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-m', '--model', default='gpt-4', help='OpenAI model')
    parser.add_argument('--chunk-pages', type=int, default=10, help='Pages per chunk')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        # Single file
        output = args.output or input_path.with_suffix('.md')
        pdf_to_markdown_codex(input_path, output, model=args.model)
        print(f"✓ Converted: {output}")
    else:
        # Directory
        batch_pdf_to_markdown(input_path, args.output, model=args.model)

if __name__ == '__main__':
    main()
```

**Save as `pdf2md.py` and use:**
```bash
# Single file
python pdf2md.py document.pdf

# Directory
python pdf2md.py /path/to/pdfs -o /path/to/markdown

# With GPT-3.5 (cheaper)
python pdf2md.py document.pdf --model gpt-3.5-turbo
```

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
# Core PDF libraries
pip install pypdf pdfplumber reportlab pytesseract pdf2image

# OpenAI Codex for PDF to Markdown conversion
pip install openai
```

System tools:
- Poppler (pdftotext, pdftoppm)
- qpdf
- pdftk
- Tesseract OCR

Environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

---

## Version History

- **1.2.0** (2026-01-04): **MAJOR UPDATE** - Added OpenAI Codex integration for PDF-to-Markdown conversion as recommended first step for all PDF processing; includes batch conversion, chunking for large files, cost-effective options, and complete CLI tool
- **1.1.0** (2026-01-02): Added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with pypdf, pdfplumber, reportlab, CLI tools
