---
name: crossprovider codex privacy-invariants-require-explicit-coherence-co
description: Privacy invariants require explicit coherence constraints
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, invariants, access-control]
---

Boolean state machines governing access control must have explicit coherence rules—don't rely on fail-open defaults. E.g., body columns cannot masquerade as metadata fields; oversized reads must fail closed; snapshots must prove residency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
