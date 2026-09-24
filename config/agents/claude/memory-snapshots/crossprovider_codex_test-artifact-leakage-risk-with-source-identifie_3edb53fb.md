---
name: crossprovider codex test-artifact-leakage-risk-with-source-identifie
description: Test artifact leakage risk with source identifiers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, leakage, test-data, privacy]
---

Test files and fixtures can be committed and later copied into comments or logs. Verify that committed test code and test data do not contain exact source labels, document names, or private path fragments. Use value-redacted fixtures and schema-only mock data rather than copied production identifiers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
