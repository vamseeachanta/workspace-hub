---
name: crossprovider codex hardened-pdf-ingest-contract-content-routing-ded
description: Hardened PDF ingest contract: content routing, dedupe, selective parsing, domain-only index updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, hardened-contract, standards-processing, workflow]
---

API/ISO standards ingest follows a 5-point hardened contract: (1) classify by extracted content/metadata, not folder label; (2) skip image-only docs to _skipped.csv + #135 vision queue; (3) dedupe-before-write by code_id/title, augment existing pages in place; (4) use provisional/raw parse status with selective verbatim only, caption-only figures; (5) update only domain index/log, never shared root files. Repeats across batches; load-bearing and codified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
