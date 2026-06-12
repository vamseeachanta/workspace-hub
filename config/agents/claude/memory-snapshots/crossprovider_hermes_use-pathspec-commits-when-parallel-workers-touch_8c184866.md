---
name: crossprovider hermes use-pathspec-commits-when-parallel-workers-touch
description: Use pathspec commits when parallel workers touch same branch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-safety, parallel-agents, workspace-hygiene, workaround]
---

Use `git commit -- <file1> <file2>...` to commit only targeted files, preserving unrelated dirty state from concurrent agents. Avoids accidental sweeps of incomplete work and preserves parallel-session safety on shared branches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
