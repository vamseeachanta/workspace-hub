---
name: crossprovider codex wrk-ids-must-remain-unique-collisions-break-line
description: WRK IDs must remain unique; collisions break lineage and automation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-queue, governance-hazard, id-collision]
---

Reusing a WRK ID for unrelated work items (e.g., WRK-309 for both 'portable Python invocation' and 'document intelligence') breaks dependency tracking, traceability, and any automation that assumes IDs are unique identifiers. Implement a pre-commit or queue-sync lint rule to reject WRK ID reuse across queue folders.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
