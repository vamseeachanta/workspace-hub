---
name: pdf-pypdf-core-pdf-operations
description: 'Sub-skill of pdf: pypdf - Core PDF Operations (+2).'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# pypdf - Core PDF Operations (+2)

## pypdf - Core PDF Operations


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


## pdfplumber - Advanced Text Extraction


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


## reportlab - Creating PDFs


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
