---
name: crossprovider codex work-queue-metadata-coherence-is-a-closure-gate
description: Work-queue metadata coherence is a closure gate
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, metadata, evidence]
---

Items marked `status: done` and `percent_complete: 100` must not have pending Close or Archive in stage_evidence.yaml; inconsistency indicates incomplete closure. All referenced evidence files must exist on disk. Flag metadata/evidence divergence before archiving, as it blocks traceability and audit trails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
