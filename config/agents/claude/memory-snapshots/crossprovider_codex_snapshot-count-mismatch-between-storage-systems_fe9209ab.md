---
name: crossprovider codex snapshot-count-mismatch-between-storage-systems
description: Snapshot count mismatch between storage systems
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [auditing, data-integrity, cross-system-coherence]
---

Report counts may come from different storage systems (e.g., local staging queue vs. tracked configs). The same number can refer to different subsets — 4,624 local files ≠ 2,252 tracked Codex snapshots. Always verify source and scope before citing totals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
