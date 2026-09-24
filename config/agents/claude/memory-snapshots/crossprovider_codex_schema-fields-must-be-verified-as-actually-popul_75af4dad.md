---
name: crossprovider codex schema-fields-must-be-verified-as-actually-popul
description: Schema fields must be verified as actually populated
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-contract, schema-verification, QA-gates]
---

If a schema field exists (e.g., `MeshQualityReport.aspect_ratio_mean`), verify empirically that the code populating it actually writes that field—not just inherits a default value. Silent defaults mask unimplemented fields; quiet QA policies that read defaults-only fields will pass when they should fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
