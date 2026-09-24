---
name: crossprovider codex proof-state-components-duplicate-provenance-rete
description: Proof-state components (duplicate, provenance, retention) must not be conflated
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, proof-state, gate-logic, defect-pattern]
---

Gate logic treats a single proof_state variable as sufficient to unblock parent issues, but duplicate-proof, provenance-proof, and retention-proof are independent conditions. Using proof_state=duplicate_matched to unblock parent #725 is unsafe if provenance and retention gates remain unmet.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
