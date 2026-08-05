---
name: crossprovider codex github-issue-labels-satisfy-approval-gates-not-j
description: GitHub issue labels satisfy approval gates, not just local markers
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [workflow, gates, approval]
---

When `.planning/plan-approved/ISSUE.md` marker is absent, check if the issue itself carries `status:plan-approved` label in GitHub; that's equally valid authorization. Approval exists in multiple forms; don't assume local file is the only source of truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
