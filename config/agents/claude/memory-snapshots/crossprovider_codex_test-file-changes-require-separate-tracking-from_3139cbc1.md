---
name: crossprovider codex test-file-changes-require-separate-tracking-from
description: Test file changes require separate tracking from source file mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, ci-cd, edge-case]
---

Session 12 identified false-confidence bug: test-commit.sh maps changed test_*.py files through source-to-test mapping, which intentionally returns nothing for test files, so modified tests never run. Tier 1 pre-commit gate needs explicit test-file detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
