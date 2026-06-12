---
name: crossprovider hermes placeholder-removal-tests-don-t-validate-impleme
description: Placeholder removal tests don't validate implementation completeness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, test-driven-development, test-scope-gaps]
---

Issue #2760: tests successfully removed old placeholder text but don't verify actual OCIMF workbook coefficients are used; implementation still hardcodes trigonometric functions (e.g., `ocimf_cx = 1.05 * abs(cos(psi))`). Test design flaw allowed incomplete engineering implementation to pass all tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
