---
name: crossprovider codex hardened-ingest-contract-five-enforcement-layers
description: Hardened ingest contract: five enforcement layers for scale
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest-contract, hardened, enforcement]
---

Contract layers: (1) content-route by actual topic not folder, (2) skip image-only/negligible-text to vision-queue + _skipped.csv (never create low-value pages), (3) dedupe-before-write (augment existing pages, don't duplicate), (4) comprehensive extraction (all tables→CSV, all figures+caption, full text structured into Scope/Definitions/Requirements/Tables/Figures/Methodology; provisional parse_status by default; >120KB → split), (5) update domain index/log, verify cross-links, don't touch root files. No commits/scripts/tooling—wiki content only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
