---
name: crossprovider codex default-values-in-data-transformation-hide-unint
description: Default values in data transformation hide unintended promotion pathways
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-flow, defaults, classification, toctou]
---

When processing records with optional fields, defaults applied in helper functions can silently promote records into unintended categories later checked downstream. Example: prior-ledger rows with missing `source_role` defaulted to `standard-candidate`, allowing non-PDF support artifacts into ingestion-candidate lists. Apply defaults only after explicit intent checks; prefer fail-closed for classification fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
