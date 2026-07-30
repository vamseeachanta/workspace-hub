---
name: crossprovider codex lifecycle-and-state-machine-validation-requires-
description: Lifecycle and state-machine validation requires negative test coverage for every transition/reason pair
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, state-machines, validation]
---

Contract-defined transitions (e.g., 'verified -> superseded requires reason=manual_override') need both positive and negative tests. Missing coverage for invalid reason/transition pairs allows silent pass-throughs. Pattern: enumerate all valid transitions in contract, then probe each invalid combination (wrong reason, forbidden transition).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
