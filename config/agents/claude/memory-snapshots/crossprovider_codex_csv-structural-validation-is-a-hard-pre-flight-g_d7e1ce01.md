---
name: crossprovider codex csv-structural-validation-is-a-hard-pre-flight-g
description: CSV structural validation is a hard pre-flight gate
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [data-export, csv, validation]
---

Malformed CSVs (header declares N fields, but data rows contain fewer) silently misalign trailing columns during parsing, corrupting metadata. Always validate row width and field consistency before exporting to Hugging Face or other platforms.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
