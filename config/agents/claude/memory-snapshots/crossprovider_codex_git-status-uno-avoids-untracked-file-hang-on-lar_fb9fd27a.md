---
name: crossprovider codex git-status-uno-avoids-untracked-file-hang-on-lar
description: git status -uno avoids untracked-file hang on large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-cli, performance, large-repos]
---

On large repos with many untracked files (llm-wiki, workspace-hub), `git status --short --branch` hangs indefinitely. Use `git status --short --branch -uno` to skip the untracked scan and complete instantly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
