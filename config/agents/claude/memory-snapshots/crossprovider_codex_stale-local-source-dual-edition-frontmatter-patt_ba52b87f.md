---
name: crossprovider codex stale-local-source-dual-edition-frontmatter-patt
description: Stale-local-source dual-edition frontmatter pattern prevents silent defects
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [standards-ingest, source-provenance, llm-wiki]
---

When local PDF source is older edition than page claims (e.g., local 4th-ed-2013 vs page claims 5th-ed-2023), carry both `source_edition_verified` and `current_edition` in frontmatter. Do not silently update page editions without source PDF verification; this defect class caused material mismatches across multiple standards pages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
