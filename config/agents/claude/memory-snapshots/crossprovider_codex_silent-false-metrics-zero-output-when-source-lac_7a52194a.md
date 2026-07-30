---
name: crossprovider codex silent-false-metrics-zero-output-when-source-lac
description: Silent false metrics (zero-output when source lacks column) are correctness defects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [data-validation, source-verification, correctness, contract-mismatch]
---

CSV/data loaders that output zeros for missing source columns (e.g., water volume) appear valid but are false data. Detect unavailable required columns during source validation and fail with clear error before writing, rather than silently emitting zeros downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
