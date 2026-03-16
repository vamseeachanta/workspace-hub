---
name: pdf-text-extractor-best-practices
description: 'Sub-skill of pdf-text-extractor: Best Practices.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Use timeout for SQLite** - `timeout=30` prevents lock errors
2. **Batch commits** - Commit every 100 files, not every file
3. **Handle errors gracefully** - Log and continue on failures
4. **Track progress** - Enable resumption of interrupted jobs
5. **Chunk appropriately** - 1500-2500 chars optimal for search
6. **Preserve page numbers** - Essential for citations
