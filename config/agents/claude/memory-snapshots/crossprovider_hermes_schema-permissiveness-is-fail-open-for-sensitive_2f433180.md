---
name: crossprovider hermes schema-permissiveness-is-fail-open-for-sensitive
description: Schema permissiveness is fail-open for sensitive-data contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-design, fail-closed-contracts, security-boundary]
---

JSON schemas without `additionalProperties: false` and without schema-level forbidden-key patterns (regex/pattern/not) allow manifests/bundles to carry inline raw data (raw_data, client_payload, source_text) while passing validation. Documented 'no inline raw data' contracts are unenforceable if the schema permits arbitrary keys. All boundary schemas need both closed-object enforcement AND negative-pattern rules prohibiting sensitive-key names.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
