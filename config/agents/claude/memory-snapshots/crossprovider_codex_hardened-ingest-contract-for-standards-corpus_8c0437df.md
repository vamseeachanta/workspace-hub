---
name: crossprovider codex hardened-ingest-contract-for-standards-corpus
description: Hardened Ingest Contract for Standards Corpus
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [corpus-ingest, standards-extraction, content-routing, quality-gates]
---

A sophisticated extraction contract emerged from scale-3 corpus work, enforcing content-routing by actual PDF topic (not publisher folder), dedupe-before-write (augment existing pages, never overwrite), content-value filtering (skip image-only scans, don't create garbage pages), and provisional-by-default table parse_status (provisional-unverified parsed or raw-unverified, never auto-verified). Off-repo PDFs referenced via source_pdf frontmatter field. Raw tables appended to domain _verification-queue.csv for human/vision review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
