---
name: crossprovider codex cold-dimension-grading-requires-strict-precedenc
description: Cold dimension grading requires strict precedence order
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [readiness-grading, cold-dimensions, version-compat]
---

For cold readiness dimensions (baseline declared, state detected), enforce strict precedence: concrete-miss > unknown > conforming. Legacy reports missing a dimension block must grade MISSING-EVIDENCE, not CONFORMS, even on absent-baseline machines, to avoid silent false-positive conformance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
