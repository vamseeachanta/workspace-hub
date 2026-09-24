---
name: crossprovider codex pathspec-commits-prevent-contamination-in-parall
description: Pathspec commits prevent contamination in parallel multi-agent work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, parallel-agents, commits]
---

When multiple agents implement against shared test files, use per-file pathspec commits (`git commit -m '...' -- file1 file2`) to ensure each agent's commit only touches its intended changes and prevent sweep contamination across worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
