---
name: semantic-search-setup-best-practices
description: 'Sub-skill of semantic-search-setup: Best Practices.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Use normalized embeddings** - Set `normalize_embeddings=True`
2. **Force CPU mode** - Set `CUDA_VISIBLE_DEVICES=""` for stability
3. **Add SQLite timeout** - Use `timeout=30` for concurrent access
4. **Process in batches** - 100-500 chunks per batch
5. **Track progress** - Save after each batch for resumability
6. **Log errors** - Capture failures for debugging
