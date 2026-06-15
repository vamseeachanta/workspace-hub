---
name: crossprovider codex dedupe-before-write-search-target-domain-s-stand
description: Dedupe-before-write: search target domain's standards/ + sources/ first
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [wiki-ingest, deduplication, workflow]
---

Before creating any wiki page, grep the TARGET domain's standards/ and sources/ directories for existing pages by code_id and title. If found, augment in place (add missing sections) rather than create duplicate. Critical gate to avoid wholesale overwrites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
