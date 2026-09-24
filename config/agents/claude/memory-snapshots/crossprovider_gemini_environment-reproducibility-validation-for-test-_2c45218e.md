---
name: crossprovider gemini environment-reproducibility-validation-for-test-
description: Environment reproducibility validation for test diagnosis
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, ci-cd, environment]
---

Verifying that local `uv run --all-extras` matches CI's install path is critical before trusting a local repro. Local missing-package or missing-fixture errors may stem from an inconsistent local environment, not the actual CI issue.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
