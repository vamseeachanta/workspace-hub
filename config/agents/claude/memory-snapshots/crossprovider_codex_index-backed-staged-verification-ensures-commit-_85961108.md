---
name: crossprovider codex index-backed-staged-verification-ensures-commit-
description: Index-backed staged verification ensures commit fidelity
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [QA, verification, commit-fidelity]
---

When verifying changed files before commit, stage only the candidate and verify against the index so verification reads exactly what would be committed, catching pathspec/staging bugs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
