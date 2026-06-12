---
name: crossprovider hermes plan-status-metadata-must-match-review-artifact-
description: Plan status metadata must match review artifact verdicts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation-drift, plan-index, status-consistency]
---

Plans marked `draft` in metadata but with completed review artifacts ready for posting create false signal. Update plan metadata (status, summary) from `draft` to `plan-review` once review synthesis recommends posting, and update the docs/plans/README.md index entry simultaneously.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
