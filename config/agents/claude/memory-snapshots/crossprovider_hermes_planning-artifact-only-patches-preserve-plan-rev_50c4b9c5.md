---
name: crossprovider hermes planning-artifact-only-patches-preserve-plan-rev
description: Planning-artifact-only patches preserve plan-review state across review cycles
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-workflow, review-cycles]
---

MAJOR review findings can be patched in planning artifacts (plan file + README) without touching implementation, keeping status in `plan-review`. Implementation remains gated until user approval of `status:plan-approved`. This pattern decouples artifact hardening from execution readiness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
