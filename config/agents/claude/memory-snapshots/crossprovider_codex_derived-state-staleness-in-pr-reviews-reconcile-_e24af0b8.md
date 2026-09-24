---
name: crossprovider codex derived-state-staleness-in-pr-reviews-reconcile-
description: Derived-state staleness in PR reviews: reconcile both origin and rebuild PRs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pr-review, derived-state, reconciliation]
---

When reviewing PRs that change source data (e.g., verification queues), verify whether a separate PR rebuilds derived state (e.g., document indices). Single-PR reviews without rebuild verification miss staleness. Reconcile both PRs and flag index staleness as MAJOR blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
