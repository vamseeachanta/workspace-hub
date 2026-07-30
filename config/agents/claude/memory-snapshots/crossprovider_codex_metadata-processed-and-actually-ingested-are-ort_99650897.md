---
name: crossprovider codex metadata-processed-and-actually-ingested-are-ort
description: Metadata-processed and actually-ingested are orthogonal verification states
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [data, architecture, validation]
---

Filesystem-present, indexed, metadata-processed (wiki inventory), and actually-ingested (corpus/document-index) are four independent facts. A corpus can be filesystem-present and indexed but have zero hits in wiki provenance targets. Each requires its own verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
