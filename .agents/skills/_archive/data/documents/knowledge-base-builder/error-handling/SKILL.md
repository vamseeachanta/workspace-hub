---
name: knowledge-base-builder-error-handling
description: 'Sub-skill of knowledge-base-builder: Error Handling.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: sqlite3.OperationalError (database is locked)**
- Cause: Concurrent access without proper timeout
- Solution: Use `timeout=30` when connecting

**Error: FTS5 not available**
- Cause: SQLite compiled without FTS5 support
- Solution: Upgrade SQLite or use FTS4 fallback

**Error: Empty search results**
- Cause: FTS index not synced with data
- Solution: Rebuild FTS index with `INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')`

**Error: Memory issues with large collections**
- Cause: Loading all chunks at once
- Solution: Process in batches, commit every 500 documents
