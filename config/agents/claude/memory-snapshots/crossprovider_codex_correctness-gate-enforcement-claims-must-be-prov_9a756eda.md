---
name: crossprovider codex correctness-gate-enforcement-claims-must-be-prov
description: Correctness gate enforcement claims must be provable with actual test commands
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, test-strategy, enforcement, correctness]
---

Plans asserting non-negotiable lint/test floors must show test commands that actually verify compliance under all supported config shapes. A command checking `v is False` without proving effective enablement under global-disable patterns leaves the floor bypassable. #2443 claimed 20-rule markdown-lint floor but step 2 didn't prove it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
