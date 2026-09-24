---
name: crossprovider codex configuration-validation-errors-must-be-marked-n
description: Configuration validation errors must be marked non-retryable to avoid wasted compute
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-classification, scheduler-behavior, operational-efficiency]
---

Validation failures with deterministic root causes (bad YAML syntax, missing required keys, type mismatches) should be classified as non-retryable errors. Retrying them wastes scheduler cycles and masks the actual blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
