---
name: crossprovider hermes exact-file-staging-prevents-silent-churn
description: Exact-file staging prevents silent churn
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, staging, commit-hygiene]
---

`git add -- <specific-paths>` commits only those files; omitting pathspec causes uv.lock, state files, and unrelated edits to bleed through. Multiple sessions saw pre-existing modifications bundled accidentally. Discipline with pathspec is load-bearing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
