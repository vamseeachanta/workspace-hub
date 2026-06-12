---
name: crossprovider hermes worktree-submodule-detection-isfile-not-isdir-fo
description: Worktree/submodule detection: isfile not isdir for .git
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-internals, worktree-hazard, repo-detection]
---

Simple `.git` directory checks fail for repos using git worktrees (where .git is a file pointing to parent/.git/worktrees/<name>) or submodules. Use `os.path.isfile('.git')` or `git rev-parse --git-dir` to detect actual git root.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
