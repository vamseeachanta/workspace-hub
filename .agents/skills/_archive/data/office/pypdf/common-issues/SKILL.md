---
name: pypdf-common-issues
description: 'Sub-skill of pypdf: Common Issues.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


#### 1. Encrypted PDF Error

```python
# Problem: Cannot read encrypted PDF
# Solution: Decrypt first

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")  # Provide password
```

#### 2. Text Extraction Returns Empty

```python
# Problem: extract_text() returns empty string
# Solution: PDF may be image-based (scanned)

# For scanned PDFs, use OCR:
# pip install pdf2image pytesseract
# Then use pytesseract to OCR the images
```

#### 3. Memory Error with Large PDFs

```python
# Problem: Memory error with large files
# Solution: Process incrementally

def split_large_pdf(input_path, output_dir, max_pages=100):
    reader = PdfReader(input_path)
    total = len(reader.pages)

    for start in range(0, total, max_pages):
        writer = PdfWriter()
        end = min(start + max_pages, total)

        for i in range(start, end):
            writer.add_page(reader.pages[i])

        writer.write(f"{output_dir}/part_{start//max_pages + 1}.pdf")
```
