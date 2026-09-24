---
name: crossprovider codex out-of-repo-shared-state-e-g-claude-projects-mem
description: Out-of-repo shared state (e.g., ~/.claude/projects/.../memory/) requires explicit sync/propagation policy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, shared-state, operational-risk]
---

Plans touching cross-machine state must cite the authoritative sync source. Operational complexity of shared-state coordination is underestimated when classified by file-count alone; T1 work touching shared state may be riskier.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
