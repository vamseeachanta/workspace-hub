---
name: crossprovider codex utility-aggregation-scripts-must-report-skipped-
description: Utility aggregation scripts must report skipped/missing data counts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-quality, auditing, observability]
---

Scripts that aggregate or audit data across multiple files should surface counts of skipped, malformed, or missing records in the output. Silent skipping makes the final metric look authoritative while actually incomplete. Report skipped counts and reasons so consumers can assess data completeness and trustworthiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
