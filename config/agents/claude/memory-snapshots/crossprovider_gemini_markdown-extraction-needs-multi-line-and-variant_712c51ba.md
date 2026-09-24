---
name: crossprovider gemini markdown-extraction-needs-multi-line-and-variant
description: Markdown extraction needs multi-line and variant-marker handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [markdown-parsing, edge-cases, extraction]
---

Line-by-line parsing with strict marker matching (`- [ ]` only) misses continuation lines and alternative markers (`* [ ]`, `+ [ ]`). Real-world markdown requires proper parser or multi-line-aware regex, not simple iteration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
