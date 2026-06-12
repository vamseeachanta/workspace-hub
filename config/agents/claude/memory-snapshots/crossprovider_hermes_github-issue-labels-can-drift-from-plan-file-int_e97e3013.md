---
name: crossprovider hermes github-issue-labels-can-drift-from-plan-file-int
description: GitHub issue labels can drift from plan file internal status
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance-drift, plan-management, issue-workflow]
---

Status labels on GitHub issues (e.g., status:plan-approved) can become out of sync with the actual status field in the corresponding plan file (e.g., plan header says 'draft'). Always verify both GitHub label AND plan file header before recommending implementation—this is governance drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
