---
name: crossprovider gemini regression-guard-tests-detect-unintended-breaks
description: Regression guard tests detect unintended breaks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tdd, testing, refactoring]
---

When extending existing infrastructure (e.g., gate contract to new providers), mix regression guards (tests on current behavior that should PASS before Phase 2) with enabler tests (tests on new behavior that should FAIL initially). Guards catch silent breaks in existing code paths when adding new features.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
