---
name: crossprovider codex hardened-contract-for-o-g-standards-corpus-inges
description: HARDENED CONTRACT for O&G standards corpus ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [corpus-ingest, standards-ingestion, llm-wiki, protocol]
---

A 5-rule protocol for full-fidelity PDF ingestion into llm-wiki: (1) route by actual semantic topic, not folder label; (2) image-only/negligible-text PDFs → _skipped.csv + #135 vision queue, never empty wiki pages; (3) dedupe-before-write by code_id + title, augment existing not duplicate; (4) selective normative verbatim only, tables marked provisional by default, raw PDFs stay off-repo; (5) update only touched domain index/log, never edit shared root files. Encodes prior scale-3 + canary lessons.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
