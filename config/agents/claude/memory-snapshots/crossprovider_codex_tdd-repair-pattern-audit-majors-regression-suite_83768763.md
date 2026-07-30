---
name: crossprovider codex tdd-repair-pattern-audit-majors-regression-suite
description: TDD repair pattern: audit → majors → regression suite → RED → implement → GREEN → verify
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [tdd, adversarial-review, defect-tracking, implementation]
---

When adversarial review finds major defects (e.g., fail-open state combinations, missing contracts), write regression tests that intentionally fail against current code, implement against that RED suite, then rerun for GREEN before advancing. Agent must verify final test exit codes are trustworthy (not summarized/partial).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
