---
name: crossprovider hermes post-commit-hooks-generate-new-dirty-state-re-ch
description: Post-commit hooks generate new dirty state—re-check git status after hooks run
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hooks, post-commit, dirty-state]
---

After a commit completes, post-commit hooks (skill-patch logging, stats generation) can create new untracked or tracked files. Before declaring a repo clean, re-run `git status`, check for `logs/orchestrator/*/`, and stage any hook-generated artifacts intended for the commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
