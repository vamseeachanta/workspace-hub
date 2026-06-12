---
name: crossprovider hermes multi-machine-topology-registry-divergence
description: Multi-machine topology registry divergence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, infrastructure, registry]
---

workspace-hub `config/workstations/registry.yaml` diverges from live state (repo locations, tool availability, mounts). Registry-sync validation should gate releases to prevent stale dispatch routing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
