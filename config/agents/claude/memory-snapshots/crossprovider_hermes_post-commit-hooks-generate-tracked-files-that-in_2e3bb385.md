---
name: crossprovider hermes post-commit-hooks-generate-tracked-files-that-in
description: Post-commit hooks generate tracked files that invalidate 'clean state' claims
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hooks, dirty-state, verification]
---

After committing, inventory hook-generated files separately; re-stage if needed. Verify `HEAD == origin/main` after pushing to confirm hooks didn't generate new commits. Do not assume `git status --porcelain` clean immediately post-commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
