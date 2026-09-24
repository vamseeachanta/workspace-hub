---
name: crossprovider codex public-surface-coverage-is-multi-class-and-requi
description: Public-surface coverage is multi-class and requires empirical git inventory verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-coverage, public-surface-classification, test-enforcement]
---

Plans claiming 'comprehensive public-surface coverage' must enumerate and test each tracked class separately: `examples/`, `.claude/`, `skills/**/*.py` (not just resources), and skill resources. Representative path tests miss drift; instead require a live `git ls-files -z` classifier test that verifies every tracked text file is included or explicitly excluded with reason.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
