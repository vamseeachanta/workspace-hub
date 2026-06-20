---
name: crossprovider codex git-status-timeouts-on-large-repos-require-bound
description: Git status timeouts on large repos require bounded per-repo checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [git, tooling, performance, audit]
---

Full `git status` calls can hang on repos with large worktrees or untracked file sets. Use timeout-bounded per-repo commands (e.g., `git diff --name-only`, `git diff --cached --name-only` with short timeouts) to avoid indefinite hangs during ecosystem audits. Split tracked/untracked enumeration if needed to keep each check fast.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
