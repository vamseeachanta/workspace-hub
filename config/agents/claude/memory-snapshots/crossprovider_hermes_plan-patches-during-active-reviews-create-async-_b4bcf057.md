---
name: crossprovider hermes plan-patches-during-active-reviews-create-async-
description: Plan patches during active reviews create async timing hazards
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-automation, plan-versioning, async-workflows, review-staleness]
---

When plans are patched iteratively while adversarial reviews are running, fresh review runs may execute against earlier plan snapshots. Results report MAJOR findings that appear stale relative to latest patches. Coordinate plan versioning with review re-run timing, or expect and document snapshot lag in review evidence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
