---
name: crossprovider codex glob-based-file-discovery-should-validate-cardin
description: Glob-based file discovery should validate cardinality, not fail silently
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-discovery, robustness, fail-loud]
---

When file-lookup patterns should match exactly one file, explicitly check matches and raise RuntimeError if zero or multiple match, rather than silently picking the first or using a fallback. This prevents nondeterministic behavior and makes configuration errors obvious.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
