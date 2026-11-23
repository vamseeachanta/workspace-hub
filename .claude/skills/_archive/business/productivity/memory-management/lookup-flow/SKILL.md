---
name: memory-management-lookup-flow
description: 'Sub-skill of memory-management: Lookup Flow.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Lookup Flow

## Lookup Flow


```
User: "ask todd about the PSR for phoenix"

1. Check CLAUDE.md (hot cache)
   → Todd? ✓ Todd Martinez, Finance
   → PSR? ✓ Pipeline Status Report
   → Phoenix? ✓ DB migration project

2. If not found → search memory/glossary.md
   → Full glossary has everyone/everything

3. If still not found → ask user
   → "What does X mean? I'll remember it."
```

This tiered approach keeps CLAUDE.md lean (~100 lines) while supporting unlimited scale in memory/.
