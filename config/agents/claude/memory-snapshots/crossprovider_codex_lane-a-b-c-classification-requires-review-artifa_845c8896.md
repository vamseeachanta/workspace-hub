---
name: crossprovider codex lane-a-b-c-classification-requires-review-artifa
description: Lane A/B/C classification requires review artifact evidence, not labels alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [continuous-planning, lane-classification, review-evidence]
---

Continuous-planning pipeline (issue #2489) gates Lane B execution on: plan file exists + review verdicts from provider artifacts + approval marker file. Label-only (`status:plan-approved`) is insufficient. Missing/empty provider review files are UNAVAILABLE-equivalent, treated as no-evidence-yet, not approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
