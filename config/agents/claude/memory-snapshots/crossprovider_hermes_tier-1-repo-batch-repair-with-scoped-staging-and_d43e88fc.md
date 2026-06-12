---
name: crossprovider hermes tier-1-repo-batch-repair-with-scoped-staging-and
description: Tier-1 repo batch repair with scoped staging and max 3 concurrent subagents
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-work, subagent-dispatch, test-repair]
---

Dispatch repo-scoped subagents in batches of 3; each subagent inventories dirty state, stages only task-owned changes (no unrelated drift), validates with canonical test command per repo, and commits. Avoid broad `git add -A`; post-commit hooks generate new files that must be re-inventoried before claiming clean state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
