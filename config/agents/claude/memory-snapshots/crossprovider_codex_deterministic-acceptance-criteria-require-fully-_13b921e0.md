---
name: crossprovider codex deterministic-acceptance-criteria-require-fully-
description: Deterministic acceptance criteria require fully specified thresholds and pinned baselines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, tdd]
---

Tests that reference undefined variables (e.g., `T7: <= N added lines`), unpinned diffs (e.g., `git diff` without base commit), or optional conditions (e.g., `test fails as expected` without clarity on whether expected-failing is acceptable) cannot be validated as part of acceptance. These criteria must be fully ground in repo state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
