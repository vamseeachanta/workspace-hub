---
name: crossprovider codex diff-based-verification-misses-untracked-files
description: Diff-based verification misses untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-tooling, verification, false-green]
---

`git diff` and `git diff --check` omit untracked files from their output. Pre-commit scripts and CI verification tools depending on these commands show false-green in greenfield projects. Either stage files before checking or add separate untracked-file enumeration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
