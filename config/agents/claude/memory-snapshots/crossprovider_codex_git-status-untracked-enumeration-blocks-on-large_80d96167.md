---
name: crossprovider codex git-status-untracked-enumeration-blocks-on-large
description: git status untracked enumeration blocks on large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, git-quirk]
---

On workspace-hub, `git status` hangs or timeouts if it enumerates untracked files. Use `git status --short --untracked-files=no` for quick branch/stash checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
