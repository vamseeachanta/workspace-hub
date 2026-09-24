---
name: crossprovider codex integration-test-snapshots-do-not-catch-edge-cas
description: Integration test snapshots do not catch edge-case robustness defects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-coverage, edge-cases]
---

Tests verifying against real scraped data are good for regression detection but miss latent failures in error handling, duplicate logic, or variant parsing. Edge-case coverage must explicitly include: missing columns, non-string values, duplicates, all-filtered results, and format variants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
