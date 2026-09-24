---
name: crossprovider codex jsonl-knowledge-schema-should-include-explicit-t
description: JSONL knowledge schema should include explicit type field for entry classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [knowledge-base, jsonl-schema, data-design]
---

Add a `type` field (e.g., `"wrk"`, `"career"`) to distinguish knowledge entry kinds. This enables type-specific filtering, display rendering, and deduplication without conflating distinct entry classes in downstream consumers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
