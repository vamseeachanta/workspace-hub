---
name: crossprovider codex security-scanners-use-fail-closed-trip-wire-sema
description: Security scanners use fail-closed trip-wire semantics, not permission gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [security, scanner-design, fail-closed]
---

Scanners should reject on any ambiguity, not permit with uncertainty. Maintain negative-assertion audit ledgers for evidence trails. Reject concrete private-field patterns regardless of whether the value is a benign placeholder.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
