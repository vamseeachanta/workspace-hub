---
name: crossprovider codex subprocess-git-invocation-inherits-process-cwd-c
description: Subprocess git invocation inherits process cwd; can capture wrong repo context
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hazard, subprocess, context-isolation]
---

Calls like `_git_revision()` run git in the process's current working directory, not the target repo. If invoked from outside the repo or in a worktree, git output (revision hash, dirty status, or None) may belong to the wrong repo. Always verify repo context or pass explicit `--git-dir`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
