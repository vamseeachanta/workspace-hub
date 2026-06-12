---
name: crossprovider codex string-pattern-health-checks-miss-pre-artifact-f
description: String-pattern health checks miss pre-artifact failures
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [monitoring, health-checks, bootstrap]
---

Health monitors relying on grep patterns of log content cannot detect failures that occur before artifact emission (bootstrap errors, missing dependencies like 'uv: not found'). A task exiting non-zero but producing only error context inside its artifact will report as false-green if the monitor doesn't capture exit codes robustly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
