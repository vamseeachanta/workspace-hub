---
name: crossprovider codex before-after-regression-testing-baseline-must-be
description: Before/after regression testing baseline must be captured at full scope before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-strategy, regression-testing, acceptance-criteria]
---

Regression acceptance criteria like 'no new test failures' require a baseline of the *full test suite* in pre-change state, not just a subset (e.g., fatigue-only collect-only). The before/after diff must cover the same scope to be meaningful. #2441 captured only fatigue collection, could not establish full-suite regression diff.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
