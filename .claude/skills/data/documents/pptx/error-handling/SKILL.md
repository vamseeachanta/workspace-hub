---
name: pptx-error-handling
description: 'Sub-skill of pptx: Error Handling.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: KeyError on placeholder**
- Cause: Placeholder index doesn't exist in layout
- Solution: List placeholders first with `slide.placeholders`

**Error: Image not found**
- Cause: Image path is incorrect
- Solution: Use absolute paths or verify relative path

**Error: Font not available**
- Cause: System font missing
- Solution: Use common fonts or embed fonts

**Error: PackageNotFoundError**
- Cause: Template file not found or corrupt
- Solution: Verify template path and file integrity
