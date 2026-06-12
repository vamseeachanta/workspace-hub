---
name: crossprovider hermes data-governance-sequencing-data-layer-first-exec
description: Data governance sequencing: data layer first, execution/report later
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, architecture, sequencing]
---

When defining multi-layer repo ecosystem architecture (data/execution/report), prioritize the data layer's canonical paths, mounts, and source-class boundaries before specifying execution and report contracts. Execution and report layers become cleaner once the source/search map is canonical.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
