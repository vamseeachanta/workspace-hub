---
name: crossprovider codex review-evidence-shape-precedent-in-continuous-pl
description: Review evidence shape precedent in continuous-planning-pipeline
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-schema, planning-workflow]
---

`scripts/ai/continuous-planning-pipeline.py:131-176` establishes `review_summary()` returning `(clean, warnings, evidence)` with `evidence['plan_sha256']` and per-provider attestations. Approval-comment standardization should reuse this shape rather than invent new evidence carriers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
