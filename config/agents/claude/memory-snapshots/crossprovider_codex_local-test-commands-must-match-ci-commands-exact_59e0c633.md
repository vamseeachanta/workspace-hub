---
name: crossprovider codex local-test-commands-must-match-ci-commands-exact
description: Local test commands must match CI commands exactly or deviations must be documented and justified
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, ci-alignment, test-strategy]
---

Plans verifying acceptance locally with different flags/markers than the actual CI pipeline cannot use local success as evidence for CI success. #2441 verified `pytest tests/ -v -m "not solver"` locally but CI uses different pytest flags, making the verification path unprovable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
