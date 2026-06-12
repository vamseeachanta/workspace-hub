---
name: crossprovider codex csv-generation-requires-csv-writer-or-equivalent
description: CSV generation requires csv.writer or equivalent, never hand-build strings
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [csv, string-handling, correctness]
---

Manual CSV string construction without escaping will fail when field values contain commas, quotes, or newlines. Always use Python's `csv.writer` module or equivalent to avoid this class of bug. Hand-built CSV without escaping is brittle and silently produces invalid output for edge cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
