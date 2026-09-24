---
name: crossprovider codex gate-readiness-must-explicitly-block-empty-missi
description: Gate readiness must explicitly block empty/missing manifest data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-logic, fail-closed, safety]
---

Scale-out/readiness gates pass empty manifests and missing required keys as 'ready' if no explicit blocker is added. Issue #504 showed empty `papers` arrays and missing keys were not fail-closed; the gate requires explicit blocker checks, not implicit silence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
