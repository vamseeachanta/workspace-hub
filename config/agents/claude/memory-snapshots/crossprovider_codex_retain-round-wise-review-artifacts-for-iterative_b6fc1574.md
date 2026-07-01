---
name: crossprovider codex retain-round-wise-review-artifacts-for-iterative
description: Retain round-wise review artifacts for iterative plan improvement
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [artifact-tracking, plan-review, reproducibility]
---

Store adversarial review results as `scripts/review/results/<plan-id>-<provider>-r<N>.md` with explicit provider and round labels. This enables tracking which issues were found/fixed in each iteration and provides historical evidence of plan quality improvement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
