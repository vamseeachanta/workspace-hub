---
name: crossprovider codex parallel-work-detection-wip-labels-and-markers
description: Parallel work detection: wip labels and markers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [git-workflow, concurrent-work, safety]
---

Check for open `wip`-labelled issues, `/tmp/.claude-wip-*` markers, and active sessions before claiming a shared checkout. Don't write to shared checkouts when parallel work is active; create fresh worktrees instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
