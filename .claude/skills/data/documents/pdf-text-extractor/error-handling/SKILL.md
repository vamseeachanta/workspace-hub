---
name: pdf-text-extractor-error-handling
description: 'Sub-skill of pdf-text-extractor: Error Handling.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: FileNotFoundError**
- Cause: PDF file path is incorrect or file doesn't exist
- Solution: Verify file path and ensure file exists

**Error: fitz.FileDataError (encrypted)**
- Cause: PDF is password-protected
- Solution: Provide password or use `doc.authenticate(password)`

**Error: Empty text extraction**
- Cause: PDF contains scanned images, not text

*See sub-skills for full details.*
