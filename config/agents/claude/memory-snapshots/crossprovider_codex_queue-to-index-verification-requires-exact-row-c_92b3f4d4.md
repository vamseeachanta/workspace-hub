---
name: crossprovider codex queue-to-index-verification-requires-exact-row-c
description: Queue-to-index verification requires exact row-count match
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [index-rebuild, queue-verification, csv-parsing]
---

When an index rebuild PR (e.g., #687) claims to fix stale rows, parse the source queue CSV directly and verify that the index rows have the exact same count and values for those rows. Embedded commas/newlines in diff text can hide mismatches. Use CSV parsing, not line-count heuristics, to catch off-by-one and summary-mismatch errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
