---
name: docx-modify-existing-document
description: 'Sub-skill of docx: Modify Existing Document (+1).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Modify Existing Document (+1)

## Modify Existing Document


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

## Add Content to Existing Document


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
