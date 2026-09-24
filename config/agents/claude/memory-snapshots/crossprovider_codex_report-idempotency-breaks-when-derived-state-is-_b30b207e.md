---
name: crossprovider codex report-idempotency-breaks-when-derived-state-is-
description: Report idempotency breaks when derived state is per-invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-engineering, idempotency, schema-design]
---

Reports that compute 'changed items' from the current run (rather than comparing pre/post filesystem state) become invocation-sensitive—identical input produces different reports on second run. Use explicit target-path vs applied-path schemas and pre/post snapshots.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
