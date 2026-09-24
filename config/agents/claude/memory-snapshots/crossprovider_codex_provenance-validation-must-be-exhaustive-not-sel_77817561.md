---
name: crossprovider codex provenance-validation-must-be-exhaustive-not-sel
description: Provenance validation must be exhaustive, not selective
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, provenance, design, completeness]
---

Validating only schema version is insufficient; all provenance fields (source data versions, scan state, config digest, code commit, key ID) and runtime configuration must be checked against actual system state. Partial validation bypasses downstream fail-closed contracts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
