---
name: crossprovider codex regression-tests-must-validate-reference-integri
description: Regression tests must validate reference integrity, not just structure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, regression, dedup]
---

For dedup acceptance, structural regression tests (paths present/absent) are incomplete; they miss broken references in other files and incomplete merged-content preservation. Add separate reference-integrity and content-preservation tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
