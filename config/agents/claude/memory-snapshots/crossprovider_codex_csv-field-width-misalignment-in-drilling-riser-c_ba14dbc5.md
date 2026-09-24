---
name: crossprovider codex csv-field-width-misalignment-in-drilling-riser-c
description: CSV field-width misalignment in drilling-riser component fixture
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, csv-validation, riser-data]
---

The canonical component CSV at `worldenergydata/tests/drilling_riser/fixtures/drilling_riser_components.csv` has 31 header columns but rows with inconsistent 29–30 fields, causing trailing provenance fields to misalign and be untrustworthy. Verify structure before consuming or republishing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
