---
name: crossprovider codex test-fixtures-are-privacy-sensitive-artifacts-in
description: Test fixtures are privacy-sensitive artifacts included in code review scope
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy, test-data, artifact-scope]
---

Test data (raw labels, exact counts, sentinel values) are part of the code artifact surface (#730/#733 test files embedded raw labels/counts that were supposed to be suppressed in outputs). Privacy reviews must scan both script outputs AND test fixtures. Generic privacy tests in tests/test_*.py are data artifacts requiring the same suppression checks as generated reports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
