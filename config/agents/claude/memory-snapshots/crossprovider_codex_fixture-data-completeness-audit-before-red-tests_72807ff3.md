---
name: crossprovider codex fixture-data-completeness-audit-before-red-tests
description: Fixture data completeness audit before RED tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, validation]
---

Before writing RED tests for behavioral changes, extract and validate the fixture schema for gaps (e.g., missing vendor metadata, incomplete well data across test suite). Trace required data to real sources; do not fabricate missing fixtures. Incomplete fixtures trap bugs in later production use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
