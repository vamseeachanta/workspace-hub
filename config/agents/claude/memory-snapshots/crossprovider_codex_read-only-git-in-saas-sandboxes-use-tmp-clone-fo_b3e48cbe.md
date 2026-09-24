---
name: crossprovider codex read-only-git-in-saas-sandboxes-use-tmp-clone-fo
description: Read-only .git/ in SaaS sandboxes: use /tmp clone for git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, sandbox, ci-cd, workaround]
---

SaaS sandboxes often mount repository `.git/` paths as read-only, blocking `git fetch`, `worktree add`, `commit`, and `push`. Workaround: clone the repository to a writable location (e.g., `/tmp`) and perform all git operations there; remove the clone when done.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
