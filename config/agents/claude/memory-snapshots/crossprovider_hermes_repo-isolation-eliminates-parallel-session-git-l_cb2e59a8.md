---
name: crossprovider hermes repo-isolation-eliminates-parallel-session-git-l
description: Repo isolation eliminates parallel-session git lock races
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git, architecture]
---

When running parallel multi-session work, use separate git repos (e.g., digitalmodel vs workspace-hub) for isolated targets. This architectural choice prevents git lock contention and commit ordering races without requiring worktrees.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
