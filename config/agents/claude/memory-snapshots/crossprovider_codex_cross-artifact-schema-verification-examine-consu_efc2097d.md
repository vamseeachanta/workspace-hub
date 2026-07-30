---
name: crossprovider codex cross-artifact-schema-verification-examine-consu
description: Cross-artifact schema verification: examine consumer code, not specification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [verification, contracts, schema, planning]
---

When validating producer-consumer handoff contracts in plans, do not verify only the stated schema specification — examine the actual consumer implementation. Executable validators in linked issues reveal schema mismatches that specifications hide. Producer and consumer key-sets must match; this can only be proven by reading actual code, not comparing written specs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
