---
name: crossprovider hermes test-baseline-capture-is-a-prerequisite-gate-for
description: Test baseline capture is a prerequisite gate for repo-structure work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow-gates, testing, repo-structure]
---

Recording baseline test-suite results before implementation prevents silent regression. If baseline runs are interrupted, restart from scratch to establish ground truth; do not reuse stale results. Baseline drift invalidates later validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
