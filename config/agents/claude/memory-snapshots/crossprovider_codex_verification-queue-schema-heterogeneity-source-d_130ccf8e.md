---
name: crossprovider codex verification-queue-schema-heterogeneity-source-d
description: Verification queue schema heterogeneity + source deny-list constraint
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [llm-wiki, schema-evolution, provenance, data-safety]
---

llm-wiki's _verification-queue.csv has mixed schemas (legacy rows have source_pdf/source_page; newer rows only page); source_pdf is resolved at render time but not persisted. Source persistence must use safe labels (source-root:og-standards/…) not local paths; repo denies `/mnt/ace/` due to data sensitivity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
