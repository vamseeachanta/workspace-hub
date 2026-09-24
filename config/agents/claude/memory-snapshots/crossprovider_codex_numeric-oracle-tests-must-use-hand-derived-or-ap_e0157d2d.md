---
name: crossprovider codex numeric-oracle-tests-must-use-hand-derived-or-ap
description: Numeric oracle tests must use hand-derived or approved-source fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, oracle-tests, fixtures]
---

Oracle tests for calculations must defer expected values until sources are approved, using hand-derived fixtures or documented sources—never production-code snapshots or interim results. This prevents oracle tests from naturalizing incorrect intermediate states.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
