---
name: document-inventory-error-handling
description: 'Sub-skill of document-inventory: Error Handling.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: PermissionError**
- Cause: Insufficient permissions to read files
- Solution: Run with appropriate permissions or skip protected files

**Error: sqlite3.OperationalError (database is locked)**
- Cause: Concurrent access without timeout
- Solution: Use `timeout=30` when connecting

**Error: UnicodeDecodeError in filenames**
- Cause: Non-UTF8 characters in file paths

*See sub-skills for full details.*
