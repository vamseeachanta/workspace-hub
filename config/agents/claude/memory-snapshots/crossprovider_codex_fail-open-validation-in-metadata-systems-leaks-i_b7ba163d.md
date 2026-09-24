---
name: crossprovider codex fail-open-validation-in-metadata-systems-leaks-i
description: Fail-open validation in metadata systems leaks invalid data downstream
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, metadata, data-integrity, gates]
---

Validation functions that only check for missing required fields (fail-open) rather than rejecting undeclared/unknown values allow bad data into canonical operations. Seen repeatedly in standards-overlap indexing: missing labels accepted, undeclared source roles defaulted, unknown source_kind values silently mapped to catch-all categories. Shift to fail-closed: explicitly reject unknown values before downstream use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
