---
name: crossprovider hermes nested-repo-pathspec-commits-avoid-unrelated-fil
description: Nested-repo pathspec commits avoid unrelated-file contamination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-hygiene, multi-repo, commit-safety, git-isolation]
---

Workspace-hub with multiple untracked generated files and deep dirty state: use explicit pathspec (`git commit -- <files>`) not `git add -A`, re-check post-commit for hook-generated dirt, verify `HEAD == origin/main`. Avoids silent sweep-contamination where parallel sessions' staged files bleed into other commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
