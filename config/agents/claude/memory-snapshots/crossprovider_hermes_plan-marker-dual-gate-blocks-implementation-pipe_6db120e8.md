---
name: crossprovider hermes plan-marker-dual-gate-blocks-implementation-pipe
description: Plan marker dual-gate blocks implementation pipeline
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-approval, dual-gate, marker-pattern, implementation-gate]
---

Issues with GitHub `status:plan-approved` label but missing local `.planning/plan-approved/<n>.md` marker file cannot proceed to implementation. The coupling between GitHub labels and local file markers creates a gate that blocks even approved plans if the marker is absent. Workaround: ensure markers are committed/pushed concurrently when approval label is applied.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
