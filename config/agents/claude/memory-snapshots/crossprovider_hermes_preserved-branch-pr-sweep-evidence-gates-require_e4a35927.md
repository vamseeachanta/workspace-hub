---
name: crossprovider hermes preserved-branch-pr-sweep-evidence-gates-require
description: Preserved-branch PR sweep: evidence gates required before merge/delete
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pr-sweep, branch-cleanup, evidence-gates]
---

During branch-to-PR conversion sweeps, never treat 'PR created' as 'branch cleaned.' Merge or delete a branch only after fresh GitHub evidence shows the PR is mergeable and all required checks are green. If CI/environment gates fail, stop, record the exact failing check names, leave branch/PR intact, and report the exact unblock step. Do not rewrite branches to rebase them during cleanup.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
