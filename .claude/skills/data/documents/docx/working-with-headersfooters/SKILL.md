---
name: docx-working-with-headersfooters
description: 'Sub-skill of docx: Working with Headers/Footers.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Working with Headers/Footers

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
