---
name: crossprovider codex review-summary-evidence-structure-for-approval-v
description: review_summary() evidence structure for approval validation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [api, verification, planning-workflow]
---

`review_summary()` in scripts/ai/continuous-planning-pipeline.py returns `(clean, warnings, evidence)` with `evidence['plan_sha256']` and per-provider data in `evidence['providers'][provider]`. Approval-request comments should validate against this exact schema rather than token-based parsing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
