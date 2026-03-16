---
name: document-inventory-best-practices
description: 'Sub-skill of document-inventory: Best Practices.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Scan before processing** - Always inventory first
2. **Use SQLite timeout** - `timeout=30` for concurrent access
3. **Batch commits** - Commit every 500 files
4. **Handle errors gracefully** - Log and continue on failures
5. **Export for review** - Generate CSV/HTML for stakeholders
6. **Update incrementally** - Use `INSERT OR REPLACE`
