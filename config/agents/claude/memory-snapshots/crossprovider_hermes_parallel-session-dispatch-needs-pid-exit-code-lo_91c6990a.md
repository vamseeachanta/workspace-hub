---
name: crossprovider hermes parallel-session-dispatch-needs-pid-exit-code-lo
description: Parallel session dispatch needs PID/exit-code logging
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-dispatch, process-tracking, monitoring]
---

Launching 3+ concurrent Claude/Codex sessions requires logging PIDs and monitoring exit codes in background logs (proc_***.log). Without PID tracking, ambiguous whether sessions completed, hung, or exited with errors.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
