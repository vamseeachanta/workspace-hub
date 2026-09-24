---
name: crossprovider codex tests-encode-verification-and-dispatch-learnings
description: Tests encode verification and dispatch learnings as regression cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, regression-cases, llm-wiki, verification, ingest]
---

llm-wiki tests (test_verify_tables.py, test_dispatch_single_pr.py, test_nonstandard_filter.py) contain regression cases encoding hard-won lessons: terminal verdict handling, deduplication precedence, conservative auto-reject logic, partial-failure PR loss. Future verification/dispatch work should audit these test cases to preserve prior insights and avoid re-discovering the same defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
