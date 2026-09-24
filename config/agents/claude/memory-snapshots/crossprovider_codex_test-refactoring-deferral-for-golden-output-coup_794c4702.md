---
name: crossprovider codex test-refactoring-deferral-for-golden-output-coup
description: Test refactoring deferral for golden-output-coupled tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, golden-files, refactoring, deferred-work]
---

Result-YAML-coupled tests shouldn't be partially mock-refactored in one work item; defer mock conversion until the comparison layer is also refactored to avoid mixed concerns and cascading YAML updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
