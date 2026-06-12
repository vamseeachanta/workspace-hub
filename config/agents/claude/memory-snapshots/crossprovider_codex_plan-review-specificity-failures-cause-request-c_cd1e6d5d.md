---
name: crossprovider codex plan-review-specificity-failures-cause-request-c
description: Plan review: specificity failures cause REQUEST_CHANGES
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, review-gates, specification]
---

Plans fail review when they lack: explicit acceptance criteria (pass/fail conditions per script), payload handling policy (truncate/reject for >5MB), platform compatibility matrix (BSD/GNU tool differences), and comprehensive edge-case test matrix. WRK-1007 plan review rejected for all four gaps; success requires section-by-section specificity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
