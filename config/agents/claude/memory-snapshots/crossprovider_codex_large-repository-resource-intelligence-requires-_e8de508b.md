---
name: crossprovider codex large-repository-resource-intelligence-requires-
description: Large repository resource intelligence requires bounded probes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operational, large-repo, performance, tooling]
---

Broad `rg --files` or `find` scans hang on large worktrees (workspace-hub, llm-wiki with 100K+ files). Resource-intel gathering succeeds with targeted grep searches, limited search depth, timeout-bounded commands, and `git status -uno` to skip untracked file enumeration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
