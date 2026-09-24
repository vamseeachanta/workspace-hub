---
name: crossprovider codex large-repository-git-operations-need-path-scopin
description: Large repository git operations need path scoping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, large-repo, git]
---

Broad git operations (`git status --untracked-files=all`, `git diff --stat`, `rg` over entire repo) timeout or run extremely slowly on workspace-hub/worldenergydata worktrees. Use path-scoped operations; stop expensive sweeps if they exceed ~1 minute without output rather than waiting for completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
