---
name: crossprovider codex verification-batch-workflow-treats-pngs-as-rende
description: Verification batch workflow treats PNGs as render scratch, not artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki-workflow, verification-batches, artifact-classification]
---

The llm-wiki verification-batch workflow convention: workers edit assigned table CSVs and return verdict TSVs; rendered PNGs from page review are process scratch, not durable repo artifacts. PNGs may be preserved via archive (`.tar.gz`) for audit trail, but should not accumulate in the repo root.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
