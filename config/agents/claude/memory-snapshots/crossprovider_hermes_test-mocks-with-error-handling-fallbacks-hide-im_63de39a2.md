---
name: crossprovider hermes test-mocks-with-error-handling-fallbacks-hide-im
description: Test mocks with error-handling fallbacks hide implementation bugs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, test-quality, shell-testing, mocking-antipatterns]
---

The mock flock in test_gsd_researcher_nightly.sh has a shift-count bug (needs shift 3, not shift 2) but tests pass because failed git operations hit `|| { ... }` fallback handlers. Tests verified error fallback paths, not success. Lesson: when mocking external tools in shell tests, verify positive-case success and command invocation, not just error-handling coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
