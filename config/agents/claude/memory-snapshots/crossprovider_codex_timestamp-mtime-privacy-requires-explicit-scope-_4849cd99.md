---
name: crossprovider codex timestamp-mtime-privacy-requires-explicit-scope-
description: Timestamp/mtime privacy requires explicit scope differentiation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, metadata, governance, testing]
---

Privacy contracts that ban 'timestamps/mtimes' in outputs must explicitly distinguish between forbidden field types (mtime, access_time, creation_time, raw numeric timestamps) and approved identifier suffixes (migration-batch labels with date components like '2026-06-17'). Conflating these creates contradictions where approved labels cannot coexist with privacy tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
