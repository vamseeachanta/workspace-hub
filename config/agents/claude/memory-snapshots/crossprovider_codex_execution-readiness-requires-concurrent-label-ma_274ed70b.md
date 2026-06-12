---
name: crossprovider codex execution-readiness-requires-concurrent-label-ma
description: Execution-readiness requires concurrent label + marker + prerequisite checks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [execution-readiness, approval-drift]
---

To classify an issue as execution-ready, verify: (a) GitHub issue open/closed state, (b) approval label present, (c) local approval-marker file exists, (d) prerequisites explicitly verified safe. Missing any of these → approval-needed or blocked, not executable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
