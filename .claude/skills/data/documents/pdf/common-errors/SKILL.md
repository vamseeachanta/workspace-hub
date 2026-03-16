---
name: pdf-common-errors
description: 'Sub-skill of pdf: Common Errors.'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# Common Errors

## Common Errors


**Error: FileNotFoundError**
- Cause: PDF file path is incorrect
- Solution: Verify file path and ensure file exists

**Error: PdfReadError (encrypted)**
- Cause: PDF is password-protected or DRM-encrypted
- Solution: Provide password or use qpdf to decrypt

**Error: Empty text extraction**
- Cause: PDF contains scanned images, not text
- Solution: Use OCR with pytesseract and pdf2image

**Error: DependencyError (Tesseract)**
- Cause: Tesseract OCR not installed
- Solution: `sudo apt-get install tesseract-ocr` or `brew install tesseract`
