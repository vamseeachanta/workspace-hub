---
name: crossprovider codex empty-diff-test-false-positives-on-pushed-commit
description: Empty-diff test false-positives on pushed commits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, ci-cd, diff-scanning]
---

Tests scanning `git diff HEAD` on a branch that's already pushed produce empty results because HEAD points to the current commit. The test passes vacuously without proving coverage of changed artifacts. Use `git diff HEAD~1` or specify the explicit commit range to scan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
