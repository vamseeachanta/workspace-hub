---
name: crossprovider codex route-b-plans-commonly-miss-full-lifecycle-stage
description: Route B plans commonly miss full lifecycle stages
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [route-b, gates, workflow, WRK-1016, WRK-1071]
---

WRK-1016/WRK-1071 both jump from implementation to verification/commit, omitting mandatory middle stages: cross-review, final-plan review, implementation cross-review. Route B gate (workflow-gatepass) requires stages 1–17; skipping them causes gate failures or forces improvisation. Include full stage sequence in plan, not just implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
