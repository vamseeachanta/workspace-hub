---
name: crossprovider codex session-lock-yaml-stores-init-pid-not-session-pi
description: session-lock.yaml stores init PID, not session PID
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-queue, sessions, liveness-detection, reliability]
---

The work-queue lock file captures the short-lived start_stage.py process PID, not a long-lived agent session PID. Liveness detection should use age-based heuristics (< 2h) rather than kill -0 PID checks to avoid false negatives.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
