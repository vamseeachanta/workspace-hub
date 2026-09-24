---
name: crossprovider codex git-diff-check-becomes-no-op-after-staging-use-c
description: git diff --check becomes no-op after staging; use --cached
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, enforcement, staging]
---

After staging files, `git diff --check` only inspects unstaged changes and misses staged content. Use `git diff --cached --check` for staged verification, and re-run immediately before commit because shared indexes remain TOCTOU surfaces.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
