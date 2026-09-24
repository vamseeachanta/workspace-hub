---
name: crossprovider codex bucket-validation-incompleteness-schema-impl-mis
description: Bucket validation incompleteness (schema/impl mismatch)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-validation, completeness, silent-breakage]
---

Plans declaring required fields (count_bucket, size_bucket, extension_bucket, date_bucket) can ship with validators only checking a subset (date_bucket, size_bucket only). Generators may accept invalid rows silently. Audit: for each declared bucket, verify validator has matching enum and tests reject invalid values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
