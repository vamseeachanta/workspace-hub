---
name: crossprovider codex hardened-llm-wiki-ingest-contract-5-rules
description: Hardened llm-wiki ingest contract (5 rules)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, ingest, contract, standards]
---

All llm-wiki standard ingest uses HARDENED contract: (1) route by topic not folder, (2) low-text → skip/vision-queue, encrypt-copyable → metadata-only, (3) dedupe-before-write, (4) selective verbatim only + PROVISIONAL-BY-DEFAULT tables, (5) update domain index/log. Subset application causes duplicates, misfiling, mislabeled parse_status; all 5 rules are load-bearing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
