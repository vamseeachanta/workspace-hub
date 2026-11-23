---
name: pdf-why-use-pdf-large-reader
description: 'Sub-skill of pdf: Why Use PDF-Large-Reader? (+8).'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# Why Use PDF-Large-Reader? (+8)

## Why Use PDF-Large-Reader?


- **Memory-efficient** - Handles 100MB+ PDFs without memory issues
- **Robust table extraction** - Handles irregular tables with column count normalization
- **Multiple output formats** - Generator (streaming), List, or Plain Text
- **Automatic strategy selection** - Intelligent chunk size calculation
- **Complete extraction** - Text, images, tables, and metadata in one pass
- **High test coverage** - 93.58% coverage with 215 tests


## Installation


```bash
# From the pdf-large-reader repository
cd /mnt/github/workspace-hub/pdf-large-reader
pip install -e .

# Or with extras
pip install -e ".[dev,progress]"
```


## Quick Start


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


## Robust Table Extraction


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


## Command Line Usage


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


## API Reference


```python
# Main entry point with automatic strategy
process_large_pdf(
    pdf_path,
    output_format="generator",    # "generator" (default), "list", or "text"
    extract_images=False,         # Extract images
    extract_tables=False,         # Extract tables with normalization
    chunk_size=None,              # Auto-calculated if None
    fallback_api_key=None,        # OpenAI API key for complex pages
    fallback_model="gpt-4.1",      # Model for fallback extraction
    progress_callback=None,       # Progress tracking function
    auto_strategy=True            # Enable automatic strategy selection
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


## PDFPage Data Structure


```python
@dataclass
class PDFPage:
    page_number: int          # Page number (1-indexed)
    text: str                 # Extracted text from page
    images: List[dict]        # Extracted images with metadata
    metadata: dict            # Page metadata including tables
```


## Performance Benchmarks


Tested on Ubuntu 22.04, Python 3.11, 16GB RAM:

| File Size | Pages | Time | Memory | Strategy |
|-----------|-------|------|--------|----------|
| 5 MB | 10 | < 5s | ~50 MB | batch_all |
| 50 MB | 100 | < 30s | ~150 MB | chunked |
| 100 MB | 500 | < 60s | ~200 MB | stream_pages |
| 200 MB | 1000 | < 2min | ~250 MB | stream_pages |


## Real-World Validation


Tested with actual API standards:
- ✅ API RP 579 (2000) - 41 MB, 966 pages
- ✅ API Std 650 (2001) - 28 MB, 461 pages
- ✅ All extraction methods working (text, auto strategy, generator, complete)
- ✅ Table extraction with column normalization
- ✅ Image extraction (461-966 images per document)
