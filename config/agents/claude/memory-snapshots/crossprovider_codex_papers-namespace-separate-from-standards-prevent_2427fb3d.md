---
name: crossprovider codex papers-namespace-separate-from-standards-prevent
description: Papers namespace separate from standards prevents routing confusion
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [corpus-ingest, routing, namespace]
---

Corpus includes both standards (ISO, API, DNV, NACE) and papers (SPE/OTC proceedings). Use separate namespace prefixes (`standards/` vs `papers/`) to avoid routing confusion. Markers like 'SPE', 'OTC', 'proceedings' indicate papers, not standards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
