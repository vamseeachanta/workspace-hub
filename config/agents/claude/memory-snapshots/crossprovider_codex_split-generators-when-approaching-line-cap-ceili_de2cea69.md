---
name: crossprovider codex split-generators-when-approaching-line-cap-ceili
description: Split generators when approaching line-cap ceilings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-structure, guardrails]
---

Monolithic ingest generators over ~399 lines should split into `*_data.py`, `*_render.py`, and `*_matrix.py` modules to stay under guardrails and improve testability. Use the split pattern early to avoid refactoring debt when adding rows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
