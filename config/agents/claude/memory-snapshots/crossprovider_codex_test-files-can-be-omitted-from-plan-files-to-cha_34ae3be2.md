---
name: crossprovider codex test-files-can-be-omitted-from-plan-files-to-cha
description: Test files can be omitted from plan 'Files to Change' scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, scope-design, plan-template]
---

Plans that list deliverable artifacts but not test files/fixtures allow TDD bypass without violating stated scope. An implementer can add production code without adding the test file if it wasn't listed. Always enumerate `tests/test_*.py` and fixture directories as explicit deliverables.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
