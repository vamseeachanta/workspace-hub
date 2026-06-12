---
name: crossprovider hermes ready-readiness-requires-implemented-artifacts-n
description: READY readiness: requires implemented artifacts, not approved plans
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness-schema, governance, stage-semantics]
---

Downstream pipeline stages (calculation_code, parametric_outputs, website_gtm) cannot be marked READY based on approved plans alone; evidence.implemented_artifacts must be populated. Approved plans without artifacts stay PARTIAL. Prevents premature governance gate closure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
