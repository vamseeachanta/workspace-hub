---
name: crossprovider gemini work-queue-stage-gates-use-immutable-commit-refe
description: Work-queue stage gates: use immutable commit references for staleness detection, not timestamps
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-gates, harness-design, determinism]
---

Timestamps are unreliable across isolated environments, repository state mutations, and stale clones. Use immutable commit references (e.g., last `plan_draft` event in append-only log) as the authoritative current state. Define the canonical current state explicitly (e.g., 'last entry in user-review-publish.yaml') with no `HEAD` or timestamp tie-break fallback.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
