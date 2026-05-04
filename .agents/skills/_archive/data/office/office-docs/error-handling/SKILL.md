---
name: office-docs-error-handling
description: 'Sub-skill of office-docs: Error Handling (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling (+2)

## Error Handling


```python
from pathlib import Path

def safe_document_generation(template_path, context, output_path):
    """Generate document with comprehensive error handling."""
    try:
        if not Path(template_path).exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        doc = DocxTemplate(template_path)

*See sub-skills for full details.*

## Temporary File Handling


```python
import tempfile
from contextlib import contextmanager

@contextmanager
def temp_document():
    """Create temporary document that auto-cleans."""
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
        temp_path = f.name
    try:
        yield temp_path
    finally:
        Path(temp_path).unlink(missing_ok=True)
```

## Streaming Large Files


```python
def process_large_excel(file_path, chunk_size=1000):
    """Process large Excel files in chunks."""
    from openpyxl import load_workbook

    wb = load_workbook(file_path, read_only=True)
    ws = wb.active

    chunk = []
    for row in ws.iter_rows(values_only=True):

*See sub-skills for full details.*
