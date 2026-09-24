---
name: crossprovider codex test-meaningfulness-requires-explicit-coverage-o
description: Test meaningfulness requires explicit coverage of authorization/unsafe paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, security-testing]
---

Tests that achieve identical collection counts and assertion totals before/after refactoring can still hide unsafe-path defects. Verify that security checks (pre-render authorization, forbidden surfaces) and edge cases (absent/empty outputs, non-executable files, directory-only forges) are covered by focused tests, not just happy-path seams.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
