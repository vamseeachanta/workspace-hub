---
name: crossprovider codex json-schemas-for-downstream-automation-must-incl
description: JSON schemas for downstream automation must include explicit failure/skip reason fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [structured-output, downstream-automation, schema-design]
---

When audit/report output is consumed by CI gates or other automation, booleans alone are insufficient. Include explicit fields like `status: pass|warn|fail|skip`, `skip_reason: null|no_pyproject|export_failed`, and optional `error` text so consumers can distinguish passing from skipped/failed without guessing or overloading enum values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
