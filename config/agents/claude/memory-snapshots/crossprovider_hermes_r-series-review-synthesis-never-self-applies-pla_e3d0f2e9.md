---
name: crossprovider hermes r-series-review-synthesis-never-self-applies-pla
description: r-series review synthesis never self-applies plan-approved label
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-workflow, approval-gate, github-labels]
---

r3 task synthesizes verdicts, updates issue state/milestone, but explicitly avoids `status:plan-approved`. User must re-open issue and approve explicitly; prevents accidental self-approval gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
