---
name: crossprovider codex process-group-liveness-is-not-equivalent-to-chil
description: Process group liveness is not equivalent to child PID state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [process-groups, pid-reuse, state-classification]
---

A supervisor intentionally holding a singleton lock while child processes drain resources looks like a stale PID if validation checks only the original child. A live process group is valid protected state, not stale-pid evidence. Supervisors must validate the process group itself (getpgrp, /proc, signals), not just the initial child PID.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
