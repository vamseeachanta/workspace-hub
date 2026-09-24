---
name: crossprovider codex ci-domain-exclusion-paths-need-explicit-harness-
description: CI domain-exclusion paths need explicit harness test coverage, not domain-matrix skip
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-testing, exclusion-paths, regression-prevention, quality-gates]
---

Paths listed in `NO_DOMAIN_PATHS` (e.g., CI workflow files, harness scripts) are excluded from the domain matrix to avoid circular tests, but must be explicitly tested by a dedicated `ci-harness-tests` job. Silently skipping these paths without dedicated coverage causes regressions. The harness job runs tests like `tests/scripts/test_detect_touched_domains.py`, `tests/workflows/automation/test_quality_gates.py` to verify excluded paths are safe.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
