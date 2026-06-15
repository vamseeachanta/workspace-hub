---
name: crossprovider codex comprehensive-extraction-structure-for-real-stan
description: Comprehensive extraction structure for real standards content
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [comprehensive-extraction, standards-ingestion, structure]
---

When extracting standards/technical PDFs: (1) all tables extracted to separate CSVs with parse_status=provisional-by-default (or raw-unverified if layout not provably faithful), (2) all figures with caption+description, (3) full normative/definitional/requirement text structured into sections (Scope, Definitions, Requirements, Tables, Figures, Methodology)—never paste raw pdftotext dumps, (4) worked examples and equations intact, (5) frontmatter includes code_id, publisher, revision, source_pdf (off-repo at /mnt/ace, never committed), visibility: private-llm-wiki, license_status.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
