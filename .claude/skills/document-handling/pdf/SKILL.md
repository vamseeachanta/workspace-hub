---
name: pdf
description: Comprehensive PDF manipulation toolkit with OpenAI Codex integration for intelligent PDF-to-Markdown conversion. IMPORTANT - Always convert PDFs to markdown first using Codex, then process the markdown. Also supports text/table extraction, PDF creation, merging/splitting, and forms. Use for all PDF document processing workflows.
version: 1.2.2
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

    # Ensure parent directory exists
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
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

    output_dir.mkdir(parents=True, exist_ok=True)

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

    # Ensure parent directory exists
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
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
```python
#!/usr/bin/env python3
"""PDF to Markdown converter using OpenAI Codex."""

import argparse
import logging
from pathlib import Path
import openai
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        temperature=0.3,
    )

    markdown_content = response.choices[0].message.content

    # Save to file
    if output_md_path is None:
        pdf_stem = Path(pdf_path).stem
        output_md_path = Path(pdf_path).parent / f"{pdf_stem}.md"

    # Ensure parent directory exists
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_md_path).write_text(markdown_content, encoding='utf-8')

    return output_md_path


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

    output_dir.mkdir(parents=True, exist_ok=True)

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


def main():
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown using OpenAI')
    parser.add_argument('input', help='PDF file or directory')
    parser.add_argument('-o', '--output', help='Output directory or file')
    parser.add_argument('-m', '--model', default='gpt-4', help='OpenAI model (gpt-4, gpt-3.5-turbo)')
    parser.add_argument('--chunk-pages', type=int, default=10, help='Pages per chunk (unused in basic mode)')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        # Single file
        output = args.output or input_path.with_suffix('.md')
        md_path = pdf_to_markdown_codex(input_path, output, model=args.model)
        print(f"✓ Converted: {md_path}")
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

## PDF-Large-Reader - Robust Extraction for Large Files

**For large PDFs (100MB+, 1000+ pages), use the pdf-large-reader library with robust table extraction.**

### Why Use PDF-Large-Reader?

- **Memory-efficient** - Handles 100MB+ PDFs without memory issues
- **Robust table extraction** - Handles irregular tables with column count normalization
- **Multiple output formats** - Generator (streaming), List, or Plain Text
- **Automatic strategy selection** - Intelligent chunk size calculation
- **Complete extraction** - Text, images, tables, and metadata in one pass
- **High test coverage** - 93.58% coverage with 215 tests

### Installation

```bash
# From the pdf-large-reader repository
cd /mnt/github/workspace-hub/pdf-large-reader
pip install -e .

# Or with extras
pip install -e ".[dev,progress]"
```

### Quick Start

```python
from pdf_large_reader import process_large_pdf, extract_text_only, extract_everything

# Simple text extraction
text = extract_text_only("large_document.pdf")
print(text)

# Process with automatic strategy selection
pages = process_large_pdf(
    "large_document.pdf",
    output_format="list",
    extract_images=True,
    extract_tables=True
)

# Memory-efficient streaming for very large files
for page in process_large_pdf("huge_file.pdf", output_format="generator"):
    print(f"Page {page.page_number}: {len(page.text)} characters")
```

### Robust Table Extraction

**NEW: Column Count Normalization (v1.3.0+)**

The table extraction now handles irregular tables with different column counts:

```python
from pdf_large_reader import extract_everything

# Extract everything including tables with robust error handling
pages = extract_everything("technical_standard.pdf")

for page in pages:
    if 'tables' in page.metadata:
        tables = page.metadata['tables']
        print(f"Page {page.page_number}: Found {len(tables)} tables")

        for i, table_df in enumerate(tables):
            print(f"  Table {i+1}: {table_df.shape[0]} rows x {table_df.shape[1]} cols")
            print(table_df.head())
```

**How It Works:**
- Detects table-like structures from text positioning
- Normalizes column counts across all rows
- Pads short rows with empty strings
- Gracefully handles malformed tables with try-except
- Logs warnings instead of crashing

**Typical Performance:**
- API Std 650 (28 MB, 461 pages): 14,648 chars/sec, 5.18 pages/sec
- API RP 579 (41 MB, 966 pages): 2,090 chars/sec, 8.48 pages/sec

### Command Line Usage

```bash
# Extract text from PDF
pdf-large-reader document.pdf

# Save to file
pdf-large-reader document.pdf --output result.txt

# Extract with images and tables
pdf-large-reader document.pdf --extract-images --extract-tables

# Use generator format for large files
pdf-large-reader huge.pdf --output-format generator

# Verbose output
pdf-large-reader document.pdf --verbose
```

### API Reference

```python
# Main entry point with automatic strategy
process_large_pdf(
    pdf_path,
    output_format="text",        # "text", "list", or "generator"
    chunk_size=None,              # Auto-calculated if None
    auto_strategy=True,           # Enable automatic strategy selection
    extract_images=False,         # Extract images
    extract_tables=False,         # Extract tables with normalization
    fallback_api_key=None,        # Claude API key for complex pages
    progress_callback=None        # Progress tracking function
)

# Quick text extraction
extract_text_only(pdf_path) -> str

# Extract with images
extract_pages_with_images(pdf_path) -> List[PDFPage]

# Extract with tables
extract_pages_with_tables(pdf_path) -> List[PDFPage]

# Extract everything
extract_everything(pdf_path) -> List[PDFPage]
```

### PDFPage Data Structure

```python
@dataclass
class PDFPage:
    page_number: int          # Page number (1-indexed)
    text: str                 # Extracted text from page
    images: List[dict]        # Extracted images with metadata
    metadata: dict            # Page metadata including tables
```

### Performance Benchmarks

Tested on Ubuntu 22.04, Python 3.11, 16GB RAM:

| File Size | Pages | Time | Memory | Strategy |
|-----------|-------|------|--------|----------|
| 5 MB | 10 | < 5s | ~50 MB | batch_all |
| 50 MB | 100 | < 30s | ~150 MB | chunked |
| 100 MB | 500 | < 60s | ~200 MB | stream_pages |
| 200 MB | 1000 | < 2min | ~250 MB | stream_pages |

### Real-World Validation

Tested with actual API standards:
- ✅ API RP 579 (2000) - 41 MB, 966 pages
- ✅ API Std 650 (2001) - 28 MB, 461 pages
- ✅ All extraction methods working (text, auto strategy, generator, complete)
- ✅ Table extraction with column normalization
- ✅ Image extraction (461-966 images per document)

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

- **1.2.2** (2026-01-04): Fixed P2 issue - added `parents=True` to all `mkdir()` calls to handle nested output paths; prevents FileNotFoundError when creating directories with non-existent parent paths
- **1.2.1** (2026-01-04): Fixed CLI tool missing imports - added complete standalone script with all required imports (openai, pypdf, logging) and function definitions; resolved P1 issue from Codex review
- **1.2.0** (2026-01-04): **MAJOR UPDATE** - Added OpenAI Codex integration for PDF-to-Markdown conversion as recommended first step for all PDF processing; includes batch conversion, chunking for large files, cost-effective options, and complete CLI tool
- **1.1.0** (2026-01-02): Added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with pypdf, pdfplumber, reportlab, CLI tools
