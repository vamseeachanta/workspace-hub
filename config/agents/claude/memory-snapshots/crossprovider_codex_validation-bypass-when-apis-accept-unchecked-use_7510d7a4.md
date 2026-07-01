---
name: crossprovider codex validation-bypass-when-apis-accept-unchecked-use
description: Validation bypass when APIs accept unchecked user-supplied payloads
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [api-design, validation, invariants, security]
---

When a strict-validation layer exists for a data type (e.g., `validate_source_catalog`), code paths accepting user-supplied values of that type should re-validate if there's a hard invariant. Accepting `catalog=` without validation bypasses the invariant guarantee.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
