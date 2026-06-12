---
name: crossprovider hermes remote-evidence-validation-must-check-schema-fie
description: Remote evidence validation must check schema fields/types, not just isinstance(dict)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [fail-closed-semantics, schema-validation, remote-evidence]
---

Code checking `isinstance(repo_placement, dict)` before trusting its fields allows malformed dicts like `{"dispatchable": "yes"}` (string instead of bool) or missing required fields to bypass fail-closed behavior. Remote readiness evidence must validate all required fields and their types explicitly before use, not rely on structural type alone.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
