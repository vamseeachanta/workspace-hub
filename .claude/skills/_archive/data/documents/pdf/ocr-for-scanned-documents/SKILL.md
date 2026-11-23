---
name: pdf-ocr-for-scanned-documents
description: 'Sub-skill of pdf: OCR for Scanned Documents (+3).'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# OCR for Scanned Documents (+3)

## OCR for Scanned Documents

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf")
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
    print(f"Page {i+1}:\n{text}")
```


## Add Watermark

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
watermark = PdfReader("watermark.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark.pages[0])
    writer.add_page(page)

writer.write("watermarked.pdf")
```


## Extract Images

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for page_num, page in enumerate(reader.pages):
    for img_num, image in enumerate(page.images):
        with open(f"image_{page_num}_{img_num}.png", "wb") as f:
            f.write(image.data)
```


## Password Protection

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.encrypt("user_password", "owner_password")
writer.write("protected.pdf")
```
