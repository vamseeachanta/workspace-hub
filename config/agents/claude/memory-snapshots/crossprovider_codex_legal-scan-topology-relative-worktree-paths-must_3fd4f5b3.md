---
name: crossprovider codex legal-scan-topology-relative-worktree-paths-must
description: Legal scan topology: relative worktree paths must match directory context exactly or scan silently scans wrong checkout
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [security, scanner-governance, topology-awareness]
---

Legal scanning commands using relative paths (e.g., ../digitalmodel/.worktrees/<issue-worktree>) depend on exact directory resolution. If the path is wrong or directory context is different, the scanner can pass against an unintended checkout. Always verify a legal scan command once before declaring it executable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
