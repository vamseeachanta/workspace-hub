---
name: crossprovider codex catalog-data-validation-thresholds-must-derive-f
description: Catalog data validation thresholds must derive from live data, not preflight assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [data-integrity, testing]
---

Plan assumed 16,300 ft/s as a literal workbook value, but inspection found 16,000 ft/s (formula result). Validators built on assumptions (e.g., `<1%` extraction gate) became invalid. Always inspect actual cells before freezing thresholds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
