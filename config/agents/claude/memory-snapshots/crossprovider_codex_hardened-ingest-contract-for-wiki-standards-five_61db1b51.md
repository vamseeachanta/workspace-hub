---
name: crossprovider codex hardened-ingest-contract-for-wiki-standards-five
description: Hardened ingest contract for wiki standards: five gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, contract, wiki, standards]
---

Full-fidelity ingest requires: (1) Content-routing by actual topic, (2) Content-value filtering (skip image-only/encrypted; encrypted → metadata-only stub), (3) Dedupe-before-write by code_id+title, (4) Selective normative verbatim only with provisional parse_status, (5) Frontmatter/link verification + enforcement scans. All five must pass before committing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
