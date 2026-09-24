---
name: crossprovider codex plan-revision-tracking-through-local-reruns-does
description: Plan revision tracking through local reruns doesn't substitute for durable artifact publication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [revision-control, artifact-durability, session-continuity]
---

Issue #2460 underwent r11→r14 refinement cycles improving approval-gate language and evidence, but all iterations remained local. Without publication to branch/GitHub, revision improvements don't compound across sessions. Future planning runs that begin with stale `status:plan-approved` surfaces need discovery-first revalidation before re-entering edit cycles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
