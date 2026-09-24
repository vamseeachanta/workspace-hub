---
name: crossprovider codex control-plane-setup-is-inconsistent-across-works
description: Control-plane setup is inconsistent across workspace child repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workspace-hygiene, control-plane, maintenance-friction]
---

Child repos show varying control-plane structure: some have full `.agent-os/.claude/.codex` sets, others only `.claude`, others only `.codex`. Root workspace-hub documents `.agent-os` but does not have it. This inconsistency increases maintenance burden and makes provider dispatch rules unclear. Consolidation is needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
