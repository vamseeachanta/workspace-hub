---
name: crossprovider hermes github-branch-cleanup-requires-fresh-state-check
description: GitHub branch cleanup requires fresh state check, not assumption from earlier PR creation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, branch-cleanup, ci-gates]
---

Never treat 'PR created' as 'branch ready to clean/delete'. Always query fresh GitHub state (`gh pr view`, `gh pr checks`) to confirm the branch is mergeable + required checks are green before merge or deletion. Stale PRs with failing CI can hide for days.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
