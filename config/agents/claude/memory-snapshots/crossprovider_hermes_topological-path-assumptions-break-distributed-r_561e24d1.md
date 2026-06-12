---
name: crossprovider hermes topological-path-assumptions-break-distributed-r
description: Topological path assumptions break distributed repo logic
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-repo, path-logic, topology]
---

Cross-repo hooks and CI logic that assume 'tier-1 repos are subdirectories under workspace-hub' fail when the actual layout is 'sibling repos alongside workspace-hub'. Verify actual repo topology before designing path-based classification, fanout, or skip logic; filesystem layout assumptions are a common failure mode.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
