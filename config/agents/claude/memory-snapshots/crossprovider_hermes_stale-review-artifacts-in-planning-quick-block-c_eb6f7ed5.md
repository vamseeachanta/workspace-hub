---
name: crossprovider hermes stale-review-artifacts-in-planning-quick-block-c
description: Stale review artifacts in .planning/quick block closure verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-artifacts, context-compaction, closure-gate]
---

Review prompt/output files cached in `.planning/quick/review-*.md` or `.planning/quick/review-*.out` can become unreliable after context compaction or tool failure. Must re-run or verify review verdicts before final commit/closeout; cached outputs can silently misreport PASS/MAJOR.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
