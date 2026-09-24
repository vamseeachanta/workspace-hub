---
name: crossprovider codex evidence-ids-drop-silently-in-aggregating-report
description: Evidence IDs drop silently in aggregating report layers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-aggregation, report-generation, traceability]
---

When collapsing structured data (scores, audit trails) to aggregated reports, composition layers may drop opaque reference IDs even when the source contains them. Preserve refs end-to-end or embed them in generated JSON artifacts so audit traces remain complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
