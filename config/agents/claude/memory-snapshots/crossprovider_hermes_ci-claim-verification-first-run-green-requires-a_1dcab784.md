---
name: crossprovider hermes ci-claim-verification-first-run-green-requires-a
description: CI claim verification: first-run-green requires actual workflow inspection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-validation, claim-verification, test-alignment]
---

Claims like "first run goes green" are false if not verified against the actual CI workflow steps. If the workflow lacks a coverage-generation step before invoking gates, the claim fails. Regression baselines must match the CI's exact test command, not a subset.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
