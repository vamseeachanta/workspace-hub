---
name: crossprovider codex ac-to-test-mapping-must-be-complete-every-accept
description: AC-to-Test mapping must be complete; every acceptance criterion requires a corresponding test including failure modes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, acceptance-criteria, test-coverage, plan-review]
---

Plans claiming 'all tests pass' but leaving acceptance criteria unmapped to tests (especially governance claims like 'Decision justified by numbers' or 'All tests pass' itself) are incomplete. TDD coverage requires failure-mode tests, not just happy-path. Test-map gaps are blocking defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
