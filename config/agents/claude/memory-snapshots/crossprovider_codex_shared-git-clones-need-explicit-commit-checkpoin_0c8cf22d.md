---
name: crossprovider codex shared-git-clones-need-explicit-commit-checkpoin
description: Shared git clones need explicit commit checkpoints before reset
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflows, shared-repositories, operational-discipline]
---

Safe pattern: branch from origin/main, verify changes, commit explicitly, then reset --hard origin/main if needed. Omitting the commit checkpoint silently loses work in shared or CI environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
