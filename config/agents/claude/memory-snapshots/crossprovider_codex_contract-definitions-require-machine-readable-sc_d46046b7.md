---
name: crossprovider codex contract-definitions-require-machine-readable-sc
description: Contract definitions require machine-readable schemas, not just prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, contracts, machine-readable, downstream-handoff]
---

When an issue defines a contract for downstream consumers to import, prose field names are insufficient. Must include JSON types, nesting rules, required/optional fields, and key grammar. Consumers cannot safely reverse-engineer these details. This was flagged MAJOR across multiple review cycles for #62's evidence schema.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
