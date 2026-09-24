---
name: crossprovider codex plan-state-drift-between-github-labels-and-local
description: Plan state-drift between GitHub labels and local files needs explicit remediation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-hazard, state-management]
---

GitHub issue labels (e.g., status:plan-approved), local frontmatter (status: plan-review), and marker files (.planning/plan-approved/NN.md) can diverge. Plans must specify which is canonical and how to resolve drift, or the review should flag the ambiguity as a blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
