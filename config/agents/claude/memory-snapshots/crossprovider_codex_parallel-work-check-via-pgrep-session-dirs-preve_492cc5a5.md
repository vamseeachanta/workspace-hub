---
name: crossprovider codex parallel-work-check-via-pgrep-session-dirs-preve
description: Parallel-work check via pgrep + session dirs prevents conflicting ingest runs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [concurrency-safety, planning-discipline, multi-agent-coordination]
---

Before planning multi-issue batch ingests, check for active workers: `pgrep -x git`, process table for session PIDs, `.claude/worktrees/` state. Parallel sessions landing on same wiki/source paths cause merge conflicts and data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
