---
name: crossprovider codex best-effort-signal-emission-pattern-always-exit-
description: Best-effort signal emission pattern—always exit 0
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, observability, reliability, bash]
---

For observability/audit tools (readiness checks, signal emitters, cost trackers), always return 0 even on failures. Log errors to stderr but never fail the pipeline. Ensures tooling doesn't cascade failures into user workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
