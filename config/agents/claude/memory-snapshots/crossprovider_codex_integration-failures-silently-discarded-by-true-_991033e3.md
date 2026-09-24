---
name: crossprovider codex integration-failures-silently-discarded-by-true-
description: Integration failures silently discarded by || true pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash-patterns, error-handling, ci-cd-gates]
---

Wiring a check with `|| true` or `|| false` discards its exit code, making failures invisible to summary counts. Failures must be captured, counted, and propagated to the final exit code or the gate becomes non-deterministic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
