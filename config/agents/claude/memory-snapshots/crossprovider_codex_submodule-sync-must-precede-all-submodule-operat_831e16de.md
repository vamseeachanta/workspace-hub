---
name: crossprovider codex submodule-sync-must-precede-all-submodule-operat
description: Submodule sync must precede all submodule operations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, submodules, prerequisites]
---

When working with git submodules in migration scripts, always run `git submodule sync --recursive` before `update --init --recursive`, even if submodules were recently pulled. Sync updates .gitmodules and remote tracking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
