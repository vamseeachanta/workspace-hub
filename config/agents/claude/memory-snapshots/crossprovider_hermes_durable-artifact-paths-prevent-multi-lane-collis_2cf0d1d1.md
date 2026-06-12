---
name: crossprovider hermes durable-artifact-paths-prevent-multi-lane-collis
description: Durable artifact paths prevent multi-lane collision
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-lane, artifact-routing, monitoring, throughput]
---

For multi-lane overnight/batch work, write prompt packs under `docs/plans/overnight-prompts/<date-or-wave>/`, results to unique per-lane files, logs to known directory. Collision-free naming + monitors checking log mtimes/output sizes verify actual progress, not just process liveness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
