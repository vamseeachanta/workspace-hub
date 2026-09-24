---
name: crossprovider codex config-source-of-truth-fragmentation-risk
description: Config source-of-truth fragmentation risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, config-management, sot]
---

workspace-hub declares repo topology in multiple places (registry.yaml, harness-config.yaml, agent config templates), and divergences create silent bugs (e.g., dev-secondary path disagreement between registry and harness-config). Future work should unify: registry.yaml as canonical source, others as derived/checked-only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
