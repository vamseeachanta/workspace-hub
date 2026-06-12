---
name: crossprovider codex timeout-tests-must-prove-bounded-runtime-process
description: Timeout tests must prove bounded runtime, process cleanup, and signal cascades
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing-rigor, timeout-behavior, process-cleanup]
---

Timeout regressions are not covered by checking for `UNAVAILABLE` substring in output; tests must assert wall-clock elapsed time, absence of surviving child processes post-timeout, and timeout-k signal cascade behavior (TERM→KILL escalation). A provider that ignores TERM must be proven killed by `-k` flag.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
