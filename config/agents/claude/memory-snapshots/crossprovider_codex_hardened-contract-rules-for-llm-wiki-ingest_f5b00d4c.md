---
name: crossprovider codex hardened-contract-rules-for-llm-wiki-ingest
description: Hardened contract rules for llm-wiki ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, ingest-workflow, content-filtering]
---

Five load-bearing rules encode scale-3 + canary lessons: (1) content-routing by topic, not folder label; (2) content-value filter—skip image-only/negligible-text PDFs to vision queue + _skipped.csv, or metadata-only for encrypted; (3) dedupe-before-write by grepping target domain standards/sources for code_id+title, augment in place if found; (4) tables PROVISIONAL-BY-DEFAULT (parse_status: provisional-unverified), append to domain's _verification-queue.csv; (5) never edit shared root files (wikis/cross-links.md, llms.txt). This workflow prevents duplicate pages, garbage entries, and overwriting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
