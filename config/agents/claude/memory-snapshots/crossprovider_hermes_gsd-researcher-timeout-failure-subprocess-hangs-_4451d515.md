---
name: crossprovider hermes gsd-researcher-timeout-failure-subprocess-hangs-
description: GSD researcher timeout failure — subprocess hangs while parent aborts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-reliability, gsd, error-handling, timeout-patterns]
---

The nightly researcher times out at 9 minutes despite a 180s script-level timeout. Root cause: Claude subprocess blocks indefinitely (likely due to context overflow + WebSearch latency) while the parent script timeout fires and kills the wrapper. Solution: increase timeout to 300s+ AND add explicit retry logic for timeout/error cases, not just malformed output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
