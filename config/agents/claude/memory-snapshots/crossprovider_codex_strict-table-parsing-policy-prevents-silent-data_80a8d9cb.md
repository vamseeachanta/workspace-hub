---
name: crossprovider codex strict-table-parsing-policy-prevents-silent-data
description: Strict table parsing policy prevents silent data corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [table-parsing, data-quality, pdf-extraction]
---

Validate table structure not just by consistent column counts, but against source PDFs. When column boundaries are uncertain or multi-row cells collapse into single rows, use raw_layout with note 'columns unverified -- needs manual/vision cleanup' rather than guessing parse semantics. Structural validation alone misses bad parses; spot-check sampled extracted tables against originals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
