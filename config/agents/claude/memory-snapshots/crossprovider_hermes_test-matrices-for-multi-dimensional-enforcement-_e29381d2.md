---
name: crossprovider hermes test-matrices-for-multi-dimensional-enforcement-
description: Test matrices for multi-dimensional enforcement modes catch documentation gaps
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-strategy, mode-matrices, enforcement, regression-coverage]
---

When testing environment-backed controls (STRICT=1/0, DISABLE=1/0), spot checks miss cross-mode failures. Need full test matrix (all combos of env vars × CLI flags) + caller-level tests proving pre-commit/pre-push/CI inherit the same precedence rule. File-presence tests give false confidence; behavior tests with mode matrices find actual bugs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
