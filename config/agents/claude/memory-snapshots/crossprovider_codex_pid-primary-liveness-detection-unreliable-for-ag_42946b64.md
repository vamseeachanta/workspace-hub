---
name: crossprovider codex pid-primary-liveness-detection-unreliable-for-ag
description: PID-primary liveness detection unreliable for agent sessions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [process-lifecycle, agent-liveness, worktree-pattern]
---

Storing short-lived PID (e.g., start_stage.py process) instead of long-running agent session PID makes `kill -0 $pid` unreliable for liveness checks—false negatives when script finishes but agent continues. Use age-based heuristics (`locked_at < 2h`) as primary liveness indicator, reserve PID checks for same-host validation only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
