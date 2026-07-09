---
name: crossprovider codex planned-public-reports-cannot-include-raw-proven
description: Planned public reports cannot include raw provenance fields blocked by governance
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [governance, artifact-schema, public-surface]
---

If governance rules block raw source_id/source_sha256 from public artifacts, a plan that proposes including those fields in the public-facing report shape will fail artifact approval. Cross-check planned output schema against governance rules before submitting for review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
