---
name: crossprovider codex uncertainty-model-changes-propagate-to-user-repo
description: Uncertainty model changes propagate to user reports
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [modeling-impact, user-facing, test-coverage]
---

Changing uncertainty models (additive → multiplicative) changes verdict headlines and report rolls—e.g., `MAJORITY` → `FULL` when low-scale DOFs no longer receive oversized noise. Audit all downstream rendering/visualization, not just the core algorithm.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
