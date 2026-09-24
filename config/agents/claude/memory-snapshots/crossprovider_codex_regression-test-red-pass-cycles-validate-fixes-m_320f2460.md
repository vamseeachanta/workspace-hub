---
name: crossprovider codex regression-test-red-pass-cycles-validate-fixes-m
description: Regression test RED→PASS cycles validate fixes more than passing-test suites
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, regression, test-design]
---

Tests written to fail on the hazard first, then fixed (e.g., test_telegram_identifier_values_are_redacted_from_freeform_strings, test_remote_evidence_secret_material_is_redacted_from_collect_readiness), caught blockers missed by initial 54-test passing suite. Design tests to expose the defect, then verify the fix.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
