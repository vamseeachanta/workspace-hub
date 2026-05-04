---
name: knowledge-base-builder-best-practices
description: 'Sub-skill of knowledge-base-builder: Best Practices.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Use SQLite timeout** - Add `timeout=30` for concurrent access
2. **Chunk appropriately** - 1000-2000 chars optimal for search
3. **Index progressively** - Process in batches for large collections
4. **Background processing** - Use service scripts for long extractions
5. **Category detection** - Auto-categorize from filename/path patterns
