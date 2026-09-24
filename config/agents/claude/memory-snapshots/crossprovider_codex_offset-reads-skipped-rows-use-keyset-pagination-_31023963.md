---
name: crossprovider codex offset-reads-skipped-rows-use-keyset-pagination-
description: OFFSET reads skipped rows; use keyset pagination instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sql, performance, pagination]
---

SQLite's OFFSET clause still evaluates (reads) the offset rows before returning the limited result, causing extra row visits. A 25-row result with OFFSET 1 can involve 26+ underlying row evaluations. Use primary-key continuation predicates (WHERE primary_key > seeded_key) for bounded queries instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
