---
name: crossprovider codex drilling-riser-csv-field-misalignment-in-worlden
description: Drilling-riser CSV field misalignment in worldenergydata
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [data-defect, worldenergydata, drilling-riser, csv]
---

The canonical 36-row drilling-riser component dataset in worldenergydata/digitalmodel has a provenance defect: 31-column header but 32 of 36 rows contain only 29–30 fields, causing trailing connector/source/notes columns to be misaligned. Must be fixed before publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
