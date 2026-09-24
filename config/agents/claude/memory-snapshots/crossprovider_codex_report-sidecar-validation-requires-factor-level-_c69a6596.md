---
name: crossprovider codex report-sidecar-validation-requires-factor-level-
description: Report sidecar validation requires factor-level provenance checks, not just top-level audit shape
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, report, provenance]
---

Report sidecars must validate both top-level audit structure AND individual factor fields (e.g., source_url presence). A malformed factor without citation URL should fail closed before the report uses it, not silently degrade. Factor-level validation catches incomplete provenance metadata that top-level checks miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
