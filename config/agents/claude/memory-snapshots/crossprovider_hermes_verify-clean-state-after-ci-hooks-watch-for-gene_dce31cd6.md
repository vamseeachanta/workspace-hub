---
name: crossprovider hermes verify-clean-state-after-ci-hooks-watch-for-gene
description: Verify clean state after CI hooks; watch for generated logs (skill-patches.jsonl)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, hooks-hygiene]
---

Post-commit/push hooks (e.g., WRK-1141) generate files like `logs/orchestrator/hermes/skill-patches.jsonl` or skill manifests. After staging task changes and committing, re-check `git status` and `git diff` to confirm hooks haven't created new dirty state before declaring repo clean.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
