---
name: crossprovider hermes untracked-test-files-block-commit-readiness
description: Untracked test files block commit readiness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, commit-hygiene, regression-coverage]
---

Regression tests added during implementation (e.g., `test_weekly_skills_audit_v2.py`) must be explicitly added to version control or they won't be included in the commit despite passing. A working tree with untracked test files is not ready for merge even if core code is correct.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
