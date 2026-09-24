---
name: crossprovider codex route-guard-logical-coherence-cannot-be-expresse
description: Route-guard logical coherence cannot be expressed in JSON schema alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, state-machines, security]
---

Fail-closed route guards require multi-field conjunction validation (e.g., 'if source_class is unknown, then ownership_state must also be unknown'). JSON schema patterns cannot express these invariants. Bypass detection: direct code-level predicate checks that reject incoherent combinations before accepting the record.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
