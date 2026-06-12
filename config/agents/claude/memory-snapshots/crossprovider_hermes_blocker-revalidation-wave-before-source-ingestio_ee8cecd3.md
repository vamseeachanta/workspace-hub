---
name: crossprovider hermes blocker-revalidation-wave-before-source-ingestio
description: Blocker revalidation wave before source ingestion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [wiki-completeness, governance, blocker-audit, pre-execution]
---

Before executing large wiki import or raw-source extraction, run governance audit to confirm blocked/approved parents are execution-ready (GitHub labels match local .planning/plan-approved/ markers). Label-only signals miss mismatches that block parent validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
