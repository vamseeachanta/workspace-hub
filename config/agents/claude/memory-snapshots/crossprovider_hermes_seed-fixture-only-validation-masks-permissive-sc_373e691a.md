---
name: crossprovider hermes seed-fixture-only-validation-masks-permissive-sc
description: Seed-fixture-only validation masks permissive schema gaps
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [TDD-anti-pattern, test-coverage-gap, schema-validation]
---

Tests that validate only the seed fixture (e.g., 'assert fixture has X') don't catch overly permissive schemas. Schema missing `additionalProperties: false` or weak `published_claims: type: array` (no item schema) passes tests because the seed fixture happens to be clean. Need separate `jsonschema.validate(bad_instance, schema)` tests to force schema strictness independent of fixture quality.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
