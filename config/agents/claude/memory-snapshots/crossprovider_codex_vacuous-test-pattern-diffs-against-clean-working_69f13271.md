---
name: crossprovider codex vacuous-test-pattern-diffs-against-clean-working
description: Vacuous test pattern: diffs against clean working tree
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, ci-cd, git]
---

Tests that verify 'changed artifacts' by checking `git diff HEAD` against a clean working tree (empty diff) are vacuous — they don't prove the committed changes were tested. Always verify against the actual changed range (e.g., `git diff origin/main HEAD` or `git diff --cached` for staged content).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
