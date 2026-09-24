---
name: crossprovider codex vacuous-test-patterns-and-guarding-validation
description: Vacuous test patterns and guarding validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, defect-class, test-isolation]
---

Tests can pass because preconditions or setup/teardown have changed, not because the guard actually works. A path-guard test that passes only because the guarded directory no longer exists does not actually validate exclusion. Real guards need isolation (e.g., monkeypatch temp directories, mock the condition in place) to verify the check works when the precondition is true.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
