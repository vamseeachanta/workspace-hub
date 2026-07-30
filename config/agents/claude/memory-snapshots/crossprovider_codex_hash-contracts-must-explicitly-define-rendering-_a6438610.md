---
name: crossprovider codex hash-contracts-must-explicitly-define-rendering-
description: Hash contracts must explicitly define rendering and null handling
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [spec-definition, hash-contracts, testing]
---

"Stable JSON" without specifying decimal precision, Unicode normalization, null encoding, and key ordering is not executable across platforms. Test suites must include golden vectors (cross-OS, field mutations, schema-version changes) and explicitly exclude self-referential fields (e.g., bundle hash from its own preimage).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
