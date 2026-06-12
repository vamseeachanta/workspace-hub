---
name: crossprovider hermes code-changes-require-artifact-regeneration-befor
description: Code changes require artifact regeneration before test interpretation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-freshness, test-integrity, generator-validation]
---

Stale artifacts after generator/validator code changes cause cascading validation failures across multiple test suites. Artifact freshness is load-bearing; must regenerate and validate before trusting test results.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
