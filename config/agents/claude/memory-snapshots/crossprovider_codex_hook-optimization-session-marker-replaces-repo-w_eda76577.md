---
name: crossprovider codex hook-optimization-session-marker-replaces-repo-w
description: Hook optimization: session marker replaces repo-wide git scans
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hooks, performance, git-optimization]
---

Repo-wide `git status`/`git diff` checks (7–10s each) exceed Stop-hook latency budget. Replace with SessionStart timestamp marker + bounded `find` for files modified after marker, pruning reference/assets trees. Verified: skill-nudge-stop reduced from 12s timeout to 3.23s.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
