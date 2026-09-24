---
name: crossprovider codex state-machine-validators-must-reject-contradicto
description: State Machine Validators Must Reject Contradictory Combinations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-machines, validation, semantic-invariants]
---

Permission-based overrides to capacity rules can produce invalid state (e.g., `status=exported` + `completeness=over-cap-unapproved`). When external evidence (permissions, approvals) can modify state transitions, validators must reject contradictory field combinations as a fail-closed invariant, not just check individual fields in isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
