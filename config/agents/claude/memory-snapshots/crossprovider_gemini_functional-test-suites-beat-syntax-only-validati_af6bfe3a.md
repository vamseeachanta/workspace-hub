---
name: crossprovider gemini functional-test-suites-beat-syntax-only-validati
description: Functional test suites beat syntax-only validation for scripts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, validation, script-quality, functional-tests]
---

Validation scripts require test coverage beyond `bash -n` syntax checks. Functional tests should verify: invalid inputs rejected (e.g., invalid WRK ID format), expected artifacts created, contradictory states caught, markdown target validation. Catches logic and integration errors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
