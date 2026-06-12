---
name: crossprovider hermes cleanup-trap-pid-reuse-race-in-provider-fanout
description: Cleanup trap PID-reuse race in provider fanout
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-safety, provider-integration, codex]
---

After waiting for background provider jobs with `wait`, must clear the `pids=()` array and disable traps with `trap - INT TERM EXIT`. Failure to do so causes subsequent fanout runs to kill unrelated processes that reuse the same PIDs. Surfaced as Gemini r3 finding in #2518 plan-review hardening.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
