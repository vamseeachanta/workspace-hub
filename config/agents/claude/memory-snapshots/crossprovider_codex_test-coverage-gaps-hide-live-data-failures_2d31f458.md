---
name: crossprovider codex test-coverage-gaps-hide-live-data-failures
description: Test coverage gaps hide live-data failures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, verification, live-data]
---

Focused tests with synthetic data can pass while live data with different characteristics (different delimiters, absolute paths, actual row counts) fails. Always verify test assumptions against live upstream data characteristics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
