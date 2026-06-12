---
name: crossprovider hermes legal-regex-patterns-trigger-on-test-fixtures
description: Legal regex patterns trigger on test fixtures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [legal-scan, false-positive, testing, regex]
---

Broad credential/secret regex scans can match pattern constants in test code (e.g., test fixtures with example paths or regex syntax). Exclude `tests/` or use allowlist + `exclude_patterns` rather than broadening `ignore_patterns`, which silently suppresses real issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
