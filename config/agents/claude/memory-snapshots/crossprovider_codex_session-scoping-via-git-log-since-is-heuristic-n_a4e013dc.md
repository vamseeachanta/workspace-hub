---
name: crossprovider codex session-scoping-via-git-log-since-is-heuristic-n
description: Session-scoping via git log --since is heuristic, not ground truth
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [session-tracking, timestamps, multi-session-context]
---

Using `git log --since "12 hours ago"` to infer "work in this session" breaks across time zones, multi-day tasks, and sessions lasting >12h. Durable session tracking requires session-start timestamp recorded in state files at session-init time, not time-window heuristics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
