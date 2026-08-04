---
name: crossprovider codex evidence-relationship-constraints-prevent-contra
description: Evidence relationship constraints prevent contradictory flag combinations
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [data-validation, invariants, fleet-state]
---

Machine classifications must enforce invariants: e.g., REACHABLE + NOT-INSTALLED + CODEX-TARGET is contradictory and should fail validation. Tests should check not just enum membership but logical consistency across evidence fields (transport, reachability, probe status, classification, checkout evidence).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
