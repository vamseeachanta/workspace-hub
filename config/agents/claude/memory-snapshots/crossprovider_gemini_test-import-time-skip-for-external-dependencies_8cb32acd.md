---
name: crossprovider gemini test-import-time-skip-for-external-dependencies
description: Test import-time skip for external dependencies
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, test-stability, external-dependencies]
---

Legacy test suites with external library dependencies can be stabilized using `pytest.importorskip`; defer deep fixes to new focused unit tests with synthetic hermetic data instead of broad refactoring.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
