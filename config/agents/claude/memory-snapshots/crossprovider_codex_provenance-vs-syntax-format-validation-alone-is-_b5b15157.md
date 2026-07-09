---
name: crossprovider codex provenance-vs-syntax-format-validation-alone-is-
description: Provenance vs syntax: format validation alone is insufficient for governance
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [governance, validation, security]
---

Recording a governance token in the format `^ams_[0-9a-f]{32}$` passes validation with any syntactically valid ID; it does not prove the token came from actual validated evidence. Governance records must cross-reference back to authoritative evidence (e.g., fixture with six manifest-key IDs), not just accept any token that matches the grammar.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
