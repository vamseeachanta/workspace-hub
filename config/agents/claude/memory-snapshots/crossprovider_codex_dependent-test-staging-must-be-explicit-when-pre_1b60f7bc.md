---
name: crossprovider codex dependent-test-staging-must-be-explicit-when-pre
description: Dependent test staging must be explicit when prerequisites are unmerged
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, test-strategy, dependencies, ci-gates]
---

Test-only plans with dependencies on unmerged issues (#601, #602) do not specify whether tests land after dependencies, are gated in CI, or marked xfail. This creates ambiguous CI behavior where tests fail intentionally. Plans must include a 'Dependency/CI Staging' section: after merge? gated? temporary xfail during transition?

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
