---
name: crossprovider codex single-authoritative-status-model-breaks-when-re
description: Single authoritative status model breaks when records classify into multiple enums
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-model, correctness, enum-collision]
---

If a status model claims "exactly one authoritative status" but code paths classify records as both `domain-mismatch` AND `gap`, the model is broken and YAML serialization becomes inconsistent. Make status handling single-path: either domain-mismatch is terminal and reported separately, or it becomes a gap with a distinct diagnostic field.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
