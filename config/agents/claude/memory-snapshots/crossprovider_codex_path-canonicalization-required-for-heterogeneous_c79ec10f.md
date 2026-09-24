---
name: crossprovider codex path-canonicalization-required-for-heterogeneous
description: Path-canonicalization required for heterogeneous corpus extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [corpus-extraction, data-pipeline, deduplication]
---

When extracting from large document collections with legacy variants (e.g., SESA LNG corpus has Old/, JWhipple/, dated transmittal folder duplicates), a deduplication/canonicalization pass must precede parser logic. This prevents parsing redundant variants and handling path-collision edge cases downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
