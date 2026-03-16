---
name: docx-basic-document-creation
description: 'Sub-skill of docx: Basic Document Creation (+3).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Basic Document Creation (+3)

## Basic Document Creation


```python
from docx import Document
from docx.shared import Pt, Inches

doc = Document()

# Add heading
doc.add_heading("Document Title", level=0)

# Add paragraph with formatting

*See sub-skills for full details.*

## Add Tables


```python
from docx import Document
from docx.shared import Inches

doc = Document()

table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'

# Fill cells

*See sub-skills for full details.*

## Add Images


```python
from docx import Document
from docx.shared import Inches

doc = Document()
doc.add_heading("Document with Image", level=0)
doc.add_picture("image.png", width=Inches(4))
doc.add_paragraph("Caption for the image.")

doc.save("output.docx")
```

## Advanced Formatting


```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Custom heading
heading = doc.add_heading(level=1)
run = heading.add_run("Custom Styled Heading")

*See sub-skills for full details.*
