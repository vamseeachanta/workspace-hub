---
name: crossprovider gemini multi-signal-eviction-for-data-governance
description: Multi-signal eviction for data governance
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-governance, compaction, lifecycle-management]
---

Effective data compaction requires independent eviction signals: completion status, path validity, temporal age, deduplication. Combining signals catches stale/orphaned data better than single rules. WRK-637 memory governance.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
