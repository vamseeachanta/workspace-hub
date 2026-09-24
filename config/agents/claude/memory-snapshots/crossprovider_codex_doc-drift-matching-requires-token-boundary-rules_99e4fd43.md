---
name: crossprovider codex doc-drift-matching-requires-token-boundary-rules
description: Doc drift matching requires token-boundary rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [quality, detection, text-matching, false-positives]
---

Naive grep-based document mention matching produces false positives (substring matches, overloaded names) and false negatives (references in code fences). Reliable drift detection needs explicit token-boundary matching and symbol-normalization rules per kind (function, class, module).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
