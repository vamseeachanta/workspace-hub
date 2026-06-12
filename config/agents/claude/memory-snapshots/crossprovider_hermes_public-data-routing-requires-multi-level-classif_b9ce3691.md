---
name: crossprovider hermes public-data-routing-requires-multi-level-classif
description: Public data routing requires multi-level classification with sanitization gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, llm-wiki, public-safety]
---

Data lifecycle has four durable levels: raw-data (never public), readable-raw-data (still private), llm-wiki-private (can feed sanitized derivatives), llm-wiki-public (only public-safe curated). Promotion between levels requires explicit sanitization/approval gate. Config and reports must track usage level to enforce boundaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
