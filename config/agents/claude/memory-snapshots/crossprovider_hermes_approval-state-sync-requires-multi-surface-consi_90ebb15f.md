---
name: crossprovider hermes approval-state-sync-requires-multi-surface-consi
description: Approval state sync requires multi-surface consistency across workers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, github-workflow, parallel-work]
---

Moving issues from plan-review → plan-approved requires coordinated updates: GitHub label + local marker (.planning/plan-approved/N.md) + plan-file header + README row. Single-surface approval drift (label set but no marker/header update) confuses parallel workers. Update all four in one commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
