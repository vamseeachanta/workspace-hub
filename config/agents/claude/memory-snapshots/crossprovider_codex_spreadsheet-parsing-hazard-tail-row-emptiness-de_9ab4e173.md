---
name: crossprovider codex spreadsheet-parsing-hazard-tail-row-emptiness-de
description: Spreadsheet parsing hazard: tail-row emptiness detection is unreliable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [data-parsing, spreadsheet-validation, edge-case]
---

Formatted Excel tail rows can contain zeros with no valid header/index columns, fooling simple 'non-empty = valid data' logic. Validate data integrity by checking required columns for semantically valid values (e.g., year must be positive integer), not just cell non-emptiness. This prevents false-positive row counts and silent corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
