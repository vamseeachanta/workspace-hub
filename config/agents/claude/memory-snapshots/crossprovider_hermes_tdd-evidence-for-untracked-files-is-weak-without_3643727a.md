---
name: crossprovider hermes tdd-evidence-for-untracked-files-is-weak-without
description: TDD evidence for untracked files is weak without git history
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, testing, git-workflow, governance]
---

For untracked implementation files, filesystem timestamps don't reliably prove tests-first order (rewrites muddy the signal, no commit history). Strong evidence: tests file exists and passes, but without git log you can't confirm TDD compliance. Governance gate should require committed test-first evidence, not rely on timestamps.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
