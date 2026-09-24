---
name: crossprovider codex edge-case-regression-must-explicitly-cover-non-t
description: Edge-case regression must explicitly cover non-target cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, edge-cases, spec-compliance, tdd]
---

Spec saying 'other statuses unchanged' requires explicit RED/GREEN covering non-target status behavior (e.g., SIGTERM 143 vs −15 when spec targets only SIGINT→130). Tests for the target case alone miss scope violations. Scope coverage assumes affirmative test of each constraint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
