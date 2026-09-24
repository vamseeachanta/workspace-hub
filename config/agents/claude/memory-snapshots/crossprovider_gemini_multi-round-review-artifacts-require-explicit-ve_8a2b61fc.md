---
name: crossprovider gemini multi-round-review-artifacts-require-explicit-ve
description: Multi-round review artifacts require explicit versioning to avoid false convergence
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [artifact-tracking, review-organization, governance]
---

Parallel or retry review sessions without deduplication create stale/duplicate artifacts that obscure decision state. #2289 uses explicit `-v1` through `-v7` versioning with revision rationale; #2459 sessions lack version tags despite apparent duplicates. Establish review-artifact convention: version tags with supersession markers so canonical source is never ambiguous and decision churn is visible.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
