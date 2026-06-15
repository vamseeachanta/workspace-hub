---
name: crossprovider codex dry-run-flags-in-cleanup-scripts-may-bypass-the-
description: Dry-run flags in cleanup scripts may bypass the run() wrapper
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, safety, scripts]
---

Some probes in daily-cleanup.sh and similar maintenance scripts can perform real operations (git worktree prune, branch deletion, network I/O) even with --dry-run if they bypass the run() wrapper. Don't assume --dry-run is safe for read-only audits; audit read-only probes must be custom.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
