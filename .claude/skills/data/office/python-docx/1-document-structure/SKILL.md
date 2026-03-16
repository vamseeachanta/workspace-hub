---
name: python-docx-1-document-structure
description: 'Sub-skill of python-docx: 1. Document Structure (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Document Structure (+3)

## 1. Document Structure


```python
"""Best practices for document organization."""

# DO: Create reusable document builders
class ReportBuilder:
    def __init__(self, template_path=None):
        self.doc = Document(template_path) if template_path else Document()

    def add_title(self, text):
        self.doc.add_heading(text, level=0)
        return self

    def add_section(self, title, content):
        self.doc.add_heading(title, level=1)
        self.doc.add_paragraph(content)
        return self

    def save(self, output_path):
        self.doc.save(output_path)

# DO: Use context managers for cleanup
from contextlib import contextmanager

@contextmanager
def document_context(output_path):
    doc = Document()
    try:
        yield doc
    finally:
        doc.save(output_path)

# Usage
with document_context('report.docx') as doc:
    doc.add_heading('Title', level=0)
    doc.add_paragraph('Content')
```


## 2. Style Consistency


```python
"""Maintain consistent styling across documents."""

# DO: Define style constants
class DocumentStyles:
    FONT_HEADING = 'Georgia'
    FONT_BODY = 'Calibri'
    SIZE_TITLE = Pt(24)
    SIZE_HEADING1 = Pt(18)
    SIZE_HEADING2 = Pt(14)
    SIZE_BODY = Pt(11)
    COLOR_PRIMARY = RGBColor(0x2E, 0x74, 0xB5)
    COLOR_SECONDARY = RGBColor(0x59, 0x59, 0x59)

# DO: Create style factory functions
def apply_heading_style(paragraph, level=1):
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    run.font.name = DocumentStyles.FONT_HEADING
    run.font.bold = True
    run.font.color.rgb = DocumentStyles.COLOR_PRIMARY

    if level == 1:
        run.font.size = DocumentStyles.SIZE_HEADING1
    elif level == 2:
        run.font.size = DocumentStyles.SIZE_HEADING2
```


## 3. Error Handling


```python
"""Robust error handling for document operations."""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def safe_generate_document(template_path, output_path, data):
    """Generate document with comprehensive error handling."""
    try:
        # Validate inputs
        if not Path(template_path).exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Generate document
        doc = Document(template_path)
        # ... processing ...
        doc.save(output_path)

        logger.info(f"Document generated: {output_path}")
        return {"success": True, "path": output_path}

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return {"success": False, "error": str(e)}

    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return {"success": False, "error": "Permission denied"}

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return {"success": False, "error": str(e)}
```


## 4. Performance Optimization


```python
"""Optimize document generation performance."""

# DO: Reuse Document objects when generating similar documents
class DocumentPool:
    def __init__(self, template_path):
        self.template_path = template_path

    def generate(self, data, output_path):
        # Load fresh copy of template for each generation
        doc = Document(self.template_path)
        # Process...
        doc.save(output_path)

# DO: Use streaming for large documents
def generate_large_table(doc, data_generator, chunk_size=1000):
    """Generate large table in chunks to manage memory."""
    table = None
    headers_added = False

    for chunk in data_generator:
        if table is None:
            headers = list(chunk[0].keys())
            table = doc.add_table(rows=1, cols=len(headers))
            for i, header in enumerate(headers):
                table.rows[0].cells[i].text = header
            headers_added = True

        for row_data in chunk:
            row = table.add_row()
            for i, value in enumerate(row_data.values()):
                row.cells[i].text = str(value)
```
