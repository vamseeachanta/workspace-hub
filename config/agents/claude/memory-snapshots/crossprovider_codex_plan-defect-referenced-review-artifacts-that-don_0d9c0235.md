---
name: crossprovider codex plan-defect-referenced-review-artifacts-that-don
description: Plan defect: referenced review artifacts that don't exist must be materialized or command-updated
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [plan-review, artifacts]
---

If a plan hard-codes a scan command pointing to a review artifact that hasn't been created yet (e.g., `scripts/review/results/2026-07-02-plan-53-codex-r2.md`), the command will fail. Either materialize the artifact or update the command to scan only existing artifacts before plan approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
