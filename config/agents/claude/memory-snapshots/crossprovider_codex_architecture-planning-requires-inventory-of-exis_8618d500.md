---
name: crossprovider codex architecture-planning-requires-inventory-of-exis
description: Architecture planning requires inventory of existing state before gap identification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture-planning, discovery-first, resource-inventory]
---

Cross-layer boundary planning (data/execution/report) must discover existing foundational artifacts first: `DATA_RESIDENCE_POLICY.md`, `mounted-source-registry.yaml`, `content-pipeline/README.md`, `WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`. Gaps are identified only after this inventory; plans must cite what was found and what remains undefined (e.g., no contract defines data→execution→report layer boundaries across `/mnt`, client projects, tier-1 repos, and wiki surfaces).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
