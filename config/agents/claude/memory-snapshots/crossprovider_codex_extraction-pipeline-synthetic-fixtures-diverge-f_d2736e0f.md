---
name: crossprovider codex extraction-pipeline-synthetic-fixtures-diverge-f
description: Extraction pipeline: synthetic fixtures diverge from live PDF data
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, sigtto-extraction, testing-gaps, pdf-parsing]
---

SIGTTO ingest tests pass on hand-crafted/fixture text but generated artifacts differ from or depend on actual PDF extraction. Risk: regeneration breaks, unverified scope claims. Pattern: unit tests do not catch PDF whitespace handling (double-spaces preserved) or layout differences (L A vs LA) that cause regen drift. Validation must run against live PDF extraction paths, not markdown surrogates or synthetic fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
