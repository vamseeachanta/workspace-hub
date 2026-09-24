---
name: crossprovider codex catalog-data-must-fail-closed-on-missing-sources
description: Catalog data must fail-closed on missing sources
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [catalog, validation, data-integrity]
---

When a catalog source (e.g., tubing workbook) is referenced in issue inventory but absent from disk, implementation must report and skip the data rather than manufacture rows. Row fabrication silently breaks downstream consumers and masks the missing source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
