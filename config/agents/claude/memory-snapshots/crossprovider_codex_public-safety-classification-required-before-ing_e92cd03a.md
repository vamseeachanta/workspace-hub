---
name: crossprovider codex public-safety-classification-required-before-ing
description: Public-safety classification required before ingesting llm-wiki source families from /mnt/ace
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [public-safety, source-classification, clearance-gates]
---

Source families under /mnt/ace default to restricted (vendor/client/private) unless explicitly classified and approved for ingestion. Safe outputs: metadata-only manifests, aggregate counts by family, generated schemas, and navigation/provenance artifacts. Raw content (standards text, vendor PDFs, client files) requires clearance gate. Approved output layers: `ingest-collection`, `raw/<safe-type>/`, `datasets/<manifest>`, `inventory/<redacted>`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
