---
name: crossprovider codex hardcoded-field-lists-in-test-fixtures-drift-fro
description: Hardcoded field lists in test fixtures drift from runtime data sources
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [fixture-management, data-source-validation, ci-testing]
---

Test data (e.g., 'all current fields in a dataset') can silently diverge when runtime extraction (workbook, API, config) changes. Validate fixture completeness in CI by comparing against the live data source, not just asserting expected count or relying on manual updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
