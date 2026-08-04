---
name: crossprovider codex pathspec-commits-prevent-auto-sync-sweep-contami
description: Pathspec commits prevent auto-sync sweep contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [git, auto-sync, commit-safety]
---

Use explicit pathspec form `git commit -F <msgfile> -- <file1> <file2>` instead of `git add -A` to prevent the working tree's dirty files from being swept into commits. Pathspec commits are immune to auto-sync's working-tree capture on unmonitored branches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
