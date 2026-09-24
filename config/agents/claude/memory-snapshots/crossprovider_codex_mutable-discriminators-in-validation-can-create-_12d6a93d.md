---
name: crossprovider codex mutable-discriminators-in-validation-can-create-
description: Mutable discriminators in validation can create coherent bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, validation-logic, security]
---

When a validator skips records based on a prefix check (e.g., `derived:` prefix) and the schema permits mutable paths, an attacker can remove the prefix, change content coherently, and recompute hashes while the validator skips the altered record. Bind discriminators immutably in schema and enforce exact path matching in validators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
