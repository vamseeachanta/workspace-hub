---
name: crossprovider codex metadata-must-be-derived-from-output-not-hardcod
description: Metadata must be derived from output, not hardcoded
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, metadata-contracts]
---

Issue #809: Generic metadata writer hardcoded format='parquet' while CORES outputs CSV, breaking downstream readers. Derive metadata from actual output or expose it as a parameter, never assume.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
