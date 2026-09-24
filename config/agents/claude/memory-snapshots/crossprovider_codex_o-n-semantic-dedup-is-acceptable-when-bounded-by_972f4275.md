---
name: crossprovider codex o-n-semantic-dedup-is-acceptable-when-bounded-by
description: O(N²) semantic dedup is acceptable when bounded by file-size cap
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, complexity-analysis, bounded-operations, dedup-algorithm]
---

Semantic deduplication can tolerate O(N²) token-overlap comparisons if files are capped at ~140 lines (~9800 max comparisons per file). Document the bound in the code as a load-bearing constant so future maintainers understand the performance trade-off.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
