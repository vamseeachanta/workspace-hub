---
name: document-rag-pipeline-error-handling
description: 'Sub-skill of document-rag-pipeline: Error Handling.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: CUDA not available**
- Cause: CUDA driver issues or incompatible GPU
- Solution: Force CPU mode with `CUDA_VISIBLE_DEVICES=""`

**Error: Tesseract not found**
- Cause: Tesseract OCR not installed
- Solution: Install with `apt-get install tesseract-ocr` or `brew install tesseract`

**Error: DRM-protected files**
- Cause: FileOpen or other DRM encryption

*See sub-skills for full details.*
