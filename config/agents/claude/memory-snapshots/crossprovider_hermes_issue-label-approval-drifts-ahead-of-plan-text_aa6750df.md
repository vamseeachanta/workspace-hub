---
name: crossprovider hermes issue-label-approval-drifts-ahead-of-plan-text
description: Issue label approval drifts ahead of plan text
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-state, github-labels, drift, launch-gate]
---

GitHub label `status:plan-approved` advances independently of plan document, which may still reserve work for future phase (e.g., #2541: label says approved, plan text says plan-review + defer extraction to separate issue). Reconcile label vs. plan before launching implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
