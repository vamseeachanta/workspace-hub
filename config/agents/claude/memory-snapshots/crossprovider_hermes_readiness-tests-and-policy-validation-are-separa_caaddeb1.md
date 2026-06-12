---
name: crossprovider hermes readiness-tests-and-policy-validation-are-separa
description: Readiness tests and policy validation are separate concerns; both needed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-coverage, schema-validation, separation-of-concerns]
---

Readiness module tests can pass while policy loader fails on live registry (e.g., schema incompatibility). Both test suites must pass independently. Readiness validates operational correctness; policy validates schema and dispatch gate logic. Passing one does not imply the other.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
