---
name: crossprovider hermes mock-tests-vs-real-workbook-tests-mocks-pass-whe
description: Mock tests vs real workbook tests: mocks pass when live invocation fails
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [mock-vs-live, integration-testing, file-parsing, test-authenticity]
---

For file-parsing tasks (OCIMF workbook extraction, coefficient parsing), mock-only tests can pass while real workbook parsing fails. Always use live test invocation with actual reference files to validate real-world behavior; reserve mocks for isolated unit tests, not integration validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
