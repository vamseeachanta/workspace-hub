---
name: crossprovider codex date-semantics-require-evidence-basis-to-prevent
description: Date semantics require evidence basis to prevent confusion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [temporal-semantics, validation, data-integrity]
---

Source data latest-date assertions must distinguish actual source data vintage from metadata refresh, file-modified, or scheduler success timestamps. Use `null` + required `source_data_latest_date_basis`/`unknown_reason` fields; prohibit metadata/file-modified clocks from populating source vintage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
