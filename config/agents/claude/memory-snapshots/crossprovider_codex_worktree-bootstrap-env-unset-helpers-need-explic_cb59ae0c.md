---
name: crossprovider codex worktree-bootstrap-env-unset-helpers-need-explic
description: Worktree bootstrap: env-unset helpers need explicit caller validation contract
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [shell, git, testing]
---

env -u GIT_DIR -u GIT_WORK_TREE works in isolated tests, but helpers returning empty on failure require callers to validate output before sourcing. Scripts copied into fixtures must be self-contained or explicitly document helper dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
