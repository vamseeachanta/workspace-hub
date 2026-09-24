---
name: crossprovider codex pre-commit-size-guards-via-git-diff-cached-and-t
description: Pre-commit size guards via git diff --cached and threshold-based blocking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, size-limits, git, pre-commit]
---

Use `git diff --cached --name-only --diff-filter=ACMR` to inspect staged files for size violations; establish hard-block and warn thresholds (90 MB block, 50 MB warn pattern documented in `.claude/hooks/check-claude-md-limits.sh`). Hook pattern is reusable across tracked state directories.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
