---
name: crossprovider hermes data-execution-report-layer-architecture-constra
description: Data/execution/report layer architecture constraints
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, data-residency, compliance, privacy]
---

Private client and public corpora combine only at retrieval/report runtime, never in intermediate layers. Execution manifests must carry input/output residency metadata. Raw generated outputs are not automatically deliverables; require provenance, legal/source review, audience-specific sanitization. /mnt/ace-data symlink confusion should be migrated/removed before architecture finalized.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
