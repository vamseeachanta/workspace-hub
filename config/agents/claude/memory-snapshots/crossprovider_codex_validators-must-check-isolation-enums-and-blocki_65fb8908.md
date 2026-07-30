---
name: crossprovider codex validators-must-check-isolation-enums-and-blocki
description: Validators must check isolation, enums, and blocking state, not just membership
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [validation-completeness, security-checks, lattice-enforcement]
---

Accepting evidence with only ID membership and 'PASS' string checks misses altered role/run/solver isolation, enum violations, and blocking-ID states. Validate the full lattice: role isolation, allowed values, blocking IDs, lifecycle state, and document identity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
