---
name: crossprovider codex cross-format-artifact-consistency-in-generated-o
description: Cross-format artifact consistency in generated outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [artifact-generation, deduplication, consistency]
---

When emitting multi-format outputs (JSONL/JSON/HTML), verify dedupe invariants are consistent across all formats and that summary counts match source data. Post-dedupe candidate lists must be identical across related artifacts, not independently deduplicated per-format.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
