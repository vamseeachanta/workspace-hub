---
name: crossprovider codex html-text-extraction-from-nested-containers-prod
description: HTML text extraction from nested containers produces duplicates and corrupts formatting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [html-parsing, text-extraction, beautifulsoup, data-corruption]
---

Walking every container (p, div) independently extracts nested text multiple times. Using get_text(strip=True) also removes spaces around inline tags, corrupting word boundaries (A <b>bold</b> test → Aboldtest). Target leaf/content nodes only and preserve word boundaries between inline markup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
