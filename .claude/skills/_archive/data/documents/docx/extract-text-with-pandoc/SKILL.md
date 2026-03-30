---
name: docx-extract-text-with-pandoc
description: 'Sub-skill of docx: Extract Text with Pandoc (+2).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Extract Text with Pandoc (+2)

## Extract Text with Pandoc


```bash
pandoc document.docx -t plain -o output.txt
pandoc document.docx -t markdown -o output.md
```

## Python Text Extraction


```python
from docx import Document

doc = Document("document.docx")
for para in doc.paragraphs:
    print(para.text)
```

## Extract Tables


```python
from docx import Document

doc = Document("document.docx")
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text, end="\t")
        print()
```
