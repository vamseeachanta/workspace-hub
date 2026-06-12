---
name: crossprovider codex csv-field-count-mismatch-silently-shifts-downstr
description: CSV field-count mismatch silently shifts downstream column alignment
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-validation, csv-parsing, structural-integrity]
---

Extra comma-delimited values in CSV rows cause parser field-count overflow, silently shifting all downstream columns for affected rows. Validation must check row field-counts match header count at ingestion, not assume structural integrity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
