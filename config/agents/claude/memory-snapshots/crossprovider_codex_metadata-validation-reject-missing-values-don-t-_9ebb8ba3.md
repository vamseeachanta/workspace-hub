---
name: crossprovider codex metadata-validation-reject-missing-values-don-t-
description: Metadata validation: reject missing values, don't default
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [validation, error-handling]
---

When a calculation mode requires metadata fields (e.g., vendor downstroke/upstroke/fluid-load), reject with exception if any is missing or null instead of defaulting to zero. Prevents silent data corruption when metadata is incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
