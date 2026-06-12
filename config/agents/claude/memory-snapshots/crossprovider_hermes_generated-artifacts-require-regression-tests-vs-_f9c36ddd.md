---
name: crossprovider hermes generated-artifacts-require-regression-tests-vs-
description: Generated artifacts require regression tests vs. live generator
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, artifact-verification, regression-detection]
---

HTML/JSON reports can drift from live code without test verification. Solution: regenerate artifact from current code during tests, compare against committed version (accounting for volatile fields like timestamps). Standalone parseability checks miss structural regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
