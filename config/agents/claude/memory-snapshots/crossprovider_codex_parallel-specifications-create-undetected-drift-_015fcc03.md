---
name: crossprovider codex parallel-specifications-create-undetected-drift-
description: Parallel specifications create undetected drift — CI workflow paths and code constants must cross-validate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [specification-duplication, drift-risk, ci-code-coherence]
---

When the same list (e.g., scan paths) appears in both CI YAML and code constants, they diverge over time without explicit cross-validation. Store the source-of-truth in code and reference it from CI, or automate a test that verifies both stay in sync.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
