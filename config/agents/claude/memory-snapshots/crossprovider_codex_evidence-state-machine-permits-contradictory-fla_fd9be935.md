---
name: crossprovider codex evidence-state-machine-permits-contradictory-fla
description: Evidence state machine permits contradictory flag states
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-machines, validation, contracts]
---

JSON schema alone cannot enforce state/flag invariants (e.g., 'deduplicated=true requires deduplication_complete=true'). Permit contradictions: `deduplicated` with `deduplication_complete=false` validates. Requires explicit allowed-transition lists or code-level guards for each state. Codex adversarial review found six such contradictions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
