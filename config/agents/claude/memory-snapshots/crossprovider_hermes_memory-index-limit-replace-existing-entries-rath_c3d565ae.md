---
name: crossprovider hermes memory-index-limit-replace-existing-entries-rath
description: Memory index limit: replace existing entries rather than append
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-management, indexing]
---

When persistent memory MEMORY.md exceeds size ceiling (~24.4KB), consolidate or condense existing entries instead of adding new ones. User prefers replacement over growth to maintain index navigability.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
