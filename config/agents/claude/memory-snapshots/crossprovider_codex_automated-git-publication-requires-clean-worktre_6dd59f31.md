---
name: crossprovider codex automated-git-publication-requires-clean-worktre
description: Automated git publication requires clean-worktree preconditions and exit-code contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [automation, git-workflow, scheduler-safety, production]
---

Scheduled tasks performing git commit && git push must define clean-worktree checks, concurrency prevention, and protection against publishing unrelated changes. Exit codes for clean/degraded/fail-closed states must be specified separately and tied to test cases; this is non-obvious and easily overlooked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
