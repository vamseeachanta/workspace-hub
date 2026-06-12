---
name: crossprovider hermes tdd-bugfix-sequence-failing-test-minimal-fix-tar
description: TDD bugfix sequence: failing test → minimal fix → targeted validation → adversarial review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, testing, workflow]
---

For bugfixes, first create a failing test proving the bug, implement the minimum fix, run the same test, then run nearby regression checks before adversarial review. This workflow catches scope creep and confirms the fix is narrow.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
