---
name: crossprovider hermes hermes-context-compaction-without-summaries-caus
description: Hermes context compaction without summaries causes repeated work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-operations, context-management, efficiency]
---

Multiple #2760 sessions showed 'Summary generation unavailable' followed by identical task-list re-reads and analysis. When compaction skips summarization, subsequent context windows re-analyze 20+ messages and duplicate effort. Monitor for this state and trigger fallback summarization.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
