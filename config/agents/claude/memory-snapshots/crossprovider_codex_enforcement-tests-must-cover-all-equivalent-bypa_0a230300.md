---
name: crossprovider codex enforcement-tests-must-cover-all-equivalent-bypa
description: Enforcement tests must cover all equivalent bypass vocabulary, not just one spelling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, enforcement, schema-validation, bypass-vocabulary]
---

When banning a bypass pattern (e.g., GitHub Actions paths filter), also reject its semantic equivalents (paths-ignore, branches-ignore) or assert the exact allowed schema. Testing only one spelling leaves equivalent violations undetected in production.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
