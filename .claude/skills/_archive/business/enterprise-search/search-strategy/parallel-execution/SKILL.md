---
name: search-strategy-parallel-execution
description: 'Sub-skill of search-strategy: Parallel Execution.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Parallel Execution

## Parallel Execution


Always execute searches across sources in parallel, never sequentially. The total search time should be roughly equal to the slowest single source, not the sum of all sources.

```
[User query]
     ↓ decompose
[~~chat query] [~~email query] [~~cloud storage query] [Wiki query] [~~project tracker query]
     ↓            ↓            ↓              ↓            ↓
  (parallel execution)
     ↓
[Merge + Rank + Deduplicate]
     ↓
[Synthesized answer]
```
