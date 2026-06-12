---
name: crossprovider hermes readme-index-deduplication-is-explicit-implement
description: README index deduplication is explicit implementation task
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance-hygiene, plan-index, deduplication]
---

`docs/plans/README.md` plan rows accumulate stale/duplicate entries over time; cleanup required during implementation to maintain single canonical row per issue. Stale rows with old status values should be removed, not left as historical record.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
