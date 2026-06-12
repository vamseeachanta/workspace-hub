---
name: crossprovider hermes cross-machine-resource-access-via-3-layer-model
description: Cross-machine resource access via 3-layer model
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, cross-machine, design, storage]
---

Recommended structure: (1) Git = control plane for registries/manifests/metadata, (2) Shared artifact store = derived outputs (summaries, indexes, extraction), (3) Local machine cache = performance layer only. Sync model: Git syncs small metadata, artifact store syncs large outputs, machines materialize only what they use.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
