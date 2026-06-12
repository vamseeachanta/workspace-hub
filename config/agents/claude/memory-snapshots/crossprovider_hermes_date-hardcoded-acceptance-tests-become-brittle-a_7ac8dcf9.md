---
name: crossprovider hermes date-hardcoded-acceptance-tests-become-brittle-a
description: Date-hardcoded acceptance tests become brittle and stale
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, acceptance, dates, fixtures]
---

Tests that hardcode expected artifact dates like `2026-05-17-report.md` fail when the tool is run on different dates. Either make expected dates configurable (e.g., via CLI flag `--date`), use relative date comparisons, or avoid hardcoding dates in test assertions. Artifact generation tools should emit current-date reports; test validation should accept any valid recent date, not a specific one.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
