---
name: crossprovider codex extraction-quality-gates-must-be-multi-dimension
description: Extraction quality gates must be multi-dimensional, not presence-based
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, quality-gates, text-extraction, llm-wiki]
---

Single-predicate checks (abstract exists, title non-default) miss corrupt extractions with control-character garbage. Combine control-character density + word/letter ratios in extracted text to fail-close on garbled PDFs. Synthetic tests pass on 3-file fixtures but real manifests require density validation on scale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
