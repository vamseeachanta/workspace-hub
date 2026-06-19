---
name: crossprovider codex large-repo-git-status-can-stall-use-narrower-com
description: Large-repo git status can stall; use narrower commands
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [git, performance, tooling]
---

On large repos, `git status` may hang or be slow. Session 3/4: `git status` stalled; narrower commands like `git diff --name-only`, `git ls-files`, and targeted file reads completed. Prefer narrow commands; wait on broad status only if necessary, stop and retry narrowly if hanging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
