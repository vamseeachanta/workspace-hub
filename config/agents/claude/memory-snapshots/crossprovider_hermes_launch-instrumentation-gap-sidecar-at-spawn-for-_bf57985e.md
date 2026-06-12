---
name: crossprovider hermes launch-instrumentation-gap-sidecar-at-spawn-for-
description: Launch instrumentation gap: sidecar-at-spawn for forensics
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [process-monitoring, instrumentation, forensics, audit-trail]
---

Local CLI process launches must write durable sidecars at spawn time: exact shell command, PID/PPID, UTC start timestamp, expected completion signals (exit code path, log marker, artifact). Without these, post-process-exit retrospective reconstruction is impossible — cannot recover PID, exact command, or final exit code after process has exited and registry is empty. Applies to `codex exec`, long-running daemons, and automation tools.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
