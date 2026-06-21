---
name: crossprovider codex fixture-state-regression-assertions-must-be-dire
description: Fixture state regression assertions must be direct, not synthetic
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [testing, fixtures, regression]
---

When authoritative fixture data (e.g., source issue labels, status snapshot) changes, tests must assert the actual fixture state changes, not just synthetic test cases of label precedence. Passing synthetic tests does not catch fixture-level regressions; need direct `assert fixture['#719']['status'] == 'implemented'` style checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
