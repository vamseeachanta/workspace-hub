---
name: crossprovider hermes tdd-evidence-is-distinct-from-test-coverage
description: TDD evidence is distinct from test coverage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, tdd, code-review]
---

Adding tests that pass is not red→green TDD. Adversarial review must look for git log evidence: failing test commit → implementation commit → passing test commit. Architecture tests verify coverage but not TDD provenance; check git history and commit messages for test-first sequence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
