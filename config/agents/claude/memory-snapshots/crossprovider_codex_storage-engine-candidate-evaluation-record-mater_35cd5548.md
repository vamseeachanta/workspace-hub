---
name: crossprovider codex storage-engine-candidate-evaluation-record-mater
description: Storage-engine candidate evaluation ≠ record materialization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [testing, privacy, performance]
---

Test instrumentation measuring predicate callbacks or index scans does not establish record-fetch bounds. A query returning 25 Python records may examine 100+ SQLite candidates internally. Separate concerns: test materialized result count and column projection (privacy contract) independently from internal query planning efficiency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
