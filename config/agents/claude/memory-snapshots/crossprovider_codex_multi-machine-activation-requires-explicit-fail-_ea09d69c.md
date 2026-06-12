---
name: crossprovider codex multi-machine-activation-requires-explicit-fail-
description: Multi-machine activation requires explicit fail-closed readiness gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-machine, governance, readiness]
---

Plans routing work to secondary machines must explicitly fail-close on missing local repo clones, auth parity, or tool availability; do not assume NFS shortcuts or undefined behavior. State exact readiness criteria (e.g., 'workspace-hub, digitalmodel, assetutilities must be cloned locally'). Do not authorize cloning/syncing in the same plan; those are separate approval gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
