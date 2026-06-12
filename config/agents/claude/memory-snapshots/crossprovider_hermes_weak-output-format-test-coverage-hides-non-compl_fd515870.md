---
name: crossprovider hermes weak-output-format-test-coverage-hides-non-compl
description: Weak output-format test coverage hides non-compliance
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, acceptance-criteria, test-gaps]
---

When acceptance criteria specify output format (e.g., six scalar plots, no heatmap), audit existing test suite — tests may not actually validate the format. Add explicit format-validation tests for edge cases. Found gap in chart-output acceptance tests during #2760 TDD.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
