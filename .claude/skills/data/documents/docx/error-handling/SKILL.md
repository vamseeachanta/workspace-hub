---
name: docx-error-handling
description: 'Sub-skill of docx: Error Handling.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: PackageNotFoundError**
- Cause: File is not a valid .docx (possibly .doc)
- Solution: Convert to .docx using LibreOffice or save as .docx from Word

**Error: KeyError on style**
- Cause: Requested style doesn't exist in document
- Solution: Use built-in styles or check available styles first

**Error: Permission denied**
- Cause: File is open in another application
- Solution: Close the file in Word/LibreOffice

**Error: Encoding issues**
- Cause: Special characters in content
- Solution: Ensure UTF-8 encoding, handle special chars
