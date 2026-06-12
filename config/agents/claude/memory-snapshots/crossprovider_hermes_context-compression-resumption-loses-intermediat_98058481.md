---
name: crossprovider hermes context-compression-resumption-loses-intermediat
description: Context compression + resumption loses intermediate reasoning; re-read memory + git state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-compression, resumption, state-coherence]
---

When context exceeds limits, Hermes compaction removes intermediate turns but preserves task list. On resumption, implicit assumption that prior work is reflected in file state can be wrong if git rebase/revert/reset occurred in parallel. Always verify git HEAD + git status + memory state before trusting prior-context summaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
