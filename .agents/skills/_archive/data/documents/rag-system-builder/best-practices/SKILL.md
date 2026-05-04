---
name: rag-system-builder-best-practices
description: 'Sub-skill of rag-system-builder: Best Practices.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Chunk size matters** - 500-1500 chars optimal for context
2. **Retrieve enough context** - top_k=5-10 for comprehensive answers
3. **Include source attribution** - Always show which documents were used
4. **Handle edge cases** - Empty results, API errors, timeouts
5. **Monitor token usage** - Track costs and optimize prompts
6. **Use SQLite timeout** - `timeout=30` for concurrent access
