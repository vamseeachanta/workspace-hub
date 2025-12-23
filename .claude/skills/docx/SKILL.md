---
name: docx
description: Comprehensive Word document toolkit for reading, creating, and editing .docx files. Supports text extraction, document creation with python-docx, and tracked changes via redlining workflow. Use for legal, academic, or professional document manipulation.
---

# DOCX Processing Skill

## Overview

This skill enables comprehensive Word document operations through multiple specialized workflows for reading, creating, and editing documents.

## Core Capabilities

- **Reading & Analysis**: Extract text via pandoc or access raw XML for comments, formatting, and metadata
- **Document Creation**: Use python-docx to build new documents from scratch
- **Document Editing**: Employ OOXML manipulation for complex modifications
- **Tracked Changes**: Implement redlining workflow for professional document editing

## Reading Documents

### Extract Text with Pandoc
```bash
pandoc document.docx -t plain -o output.txt
pandoc document.docx -t markdown -o output.md
```

### Python Text Extraction
```python
from docx import Document

doc = Document("document.docx")
for para in doc.paragraphs:
    print(para.text)
```

### Extract Tables
```python
from docx import Document

doc = Document("document.docx")
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text, end="\t")
        print()
```

## Creating Documents

### Basic Document Creation
```python
from docx import Document
from docx.shared import Pt, Inches

doc = Document()

# Add heading
doc.add_heading("Document Title", level=0)

# Add paragraph with formatting
para = doc.add_paragraph()
run = para.add_run("Bold text")
run.bold = True

para.add_run(" and ")
run = para.add_run("italic text")
run.italic = True

# Add styled paragraph
doc.add_paragraph("Normal paragraph text.")

doc.save("output.docx")
```

### Add Tables
```python
from docx import Document
from docx.shared import Inches

doc = Document()

table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'

# Fill cells
for i, row in enumerate(table.rows):
    for j, cell in enumerate(row.cells):
        cell.text = f"Row {i+1}, Col {j+1}"

doc.save("output.docx")
```

### Add Images
```python
from docx import Document
from docx.shared import Inches

doc = Document()
doc.add_heading("Document with Image", level=0)
doc.add_picture("image.png", width=Inches(4))
doc.add_paragraph("Caption for the image.")

doc.save("output.docx")
```

### Advanced Formatting
```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Custom heading
heading = doc.add_heading(level=1)
run = heading.add_run("Custom Styled Heading")
run.font.size = Pt(24)
run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

# Centered paragraph
para = doc.add_paragraph("Centered text")
para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Bulleted list
doc.add_paragraph("First item", style='List Bullet')
doc.add_paragraph("Second item", style='List Bullet')
doc.add_paragraph("Third item", style='List Bullet')

doc.save("output.docx")
```

## Editing Documents

### Modify Existing Document
```python
from docx import Document

doc = Document("existing.docx")

# Replace text in paragraphs
for para in doc.paragraphs:
    if "old text" in para.text:
        for run in para.runs:
            run.text = run.text.replace("old text", "new text")

doc.save("modified.docx")
```

### Add Content to Existing Document
```python
from docx import Document

doc = Document("existing.docx")

# Add new paragraph at end
doc.add_paragraph("New paragraph added.")

# Add new section
doc.add_page_break()
doc.add_heading("New Section", level=1)
doc.add_paragraph("Content for new section.")

doc.save("modified.docx")
```

## Redlining Workflow

For legal, academic, or government documents requiring tracked changes:

### Step 1: Convert to Markdown
```bash
pandoc document.docx -t markdown -o document.md
```

### Step 2: Plan Changes
Document the specific changes needed before implementation.

### Step 3: Apply Changes in Batches
Apply 3-10 related modifications at a time, preserving formatting.

### Step 4: Validate Changes
Ensure original formatting and unchanged content are preserved.

### Key Principle
When modifying text like "30 days" to "60 days", only mark the changed portion while preserving unchanged runs with their original RSID attributes.

## Extract Metadata
```python
from docx import Document

doc = Document("document.docx")
props = doc.core_properties

print(f"Title: {props.title}")
print(f"Author: {props.author}")
print(f"Created: {props.created}")
print(f"Modified: {props.modified}")
print(f"Last Modified By: {props.last_modified_by}")
```

## Working with Headers/Footers
```python
from docx import Document

doc = Document()

# Add header
section = doc.sections[0]
header = section.header
header_para = header.paragraphs[0]
header_para.text = "Document Header"

# Add footer
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.text = "Page Footer"

doc.save("with_header_footer.docx")
```

## Dependencies

```bash
pip install python-docx
```

System tools:
- Pandoc (for format conversion)
- LibreOffice (for PDF conversion)
