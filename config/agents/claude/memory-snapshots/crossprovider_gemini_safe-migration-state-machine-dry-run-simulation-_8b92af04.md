---
name: crossprovider gemini safe-migration-state-machine-dry-run-simulation-
description: Safe migration state machine: dry-run → simulation → apply → verify idempotency
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, state-machine, idempotency, compliance]
---

Migrations use explicit state transitions (pre-wave → wave-applied → partial-applied with rollback). Require approval artifacts at each gate (APPROVED_FOR_DRYRUN, APPROVED_FOR_SIMULATION, APPROVED). Second apply on same state must be a no-op. Prevents partial-apply corruption.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
