---
name: crossprovider hermes detect-stale-review-artifacts-by-comparing-again
description: Detect stale review artifacts by comparing against live handoff evidence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, plan-verification, artifact-staleness, evidence-based]
---

When reviewing old plans or artifacts, verify against live handoff/evidence (newer review rounds, diff logs, current git state) to catch staleness; static file reads can mask changes between plan versions. Compare line counts, section headers, and referenced line numbers against current state before accepting review input.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
