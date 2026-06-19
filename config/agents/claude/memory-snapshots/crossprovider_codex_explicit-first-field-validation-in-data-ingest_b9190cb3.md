---
name: crossprovider codex explicit-first-field-validation-in-data-ingest
description: Explicit-first field validation in data ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [data-ingest, validation, field-defaults]
---

When processing records with optional/legacy fields, validate explicit field presence before applying fallbacks. Missing fields should not default to broad acceptance categories; they should fail safe or require additional constraints to prevent low-confidence artifacts from leaking into generated outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
