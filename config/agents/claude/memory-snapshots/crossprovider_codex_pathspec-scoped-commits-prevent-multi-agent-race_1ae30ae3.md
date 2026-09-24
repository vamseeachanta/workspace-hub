---
name: crossprovider codex pathspec-scoped-commits-prevent-multi-agent-race
description: Pathspec-scoped commits prevent multi-agent race contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, multi-agent, safety]
---

Use `git commit -m "..." -- <file>` form to limit commit scope to specific files; forces explicit file inclusion and prevents accidental sweep of unrelated changes. Essential when parallel agents commit to the same repo with isolated worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
