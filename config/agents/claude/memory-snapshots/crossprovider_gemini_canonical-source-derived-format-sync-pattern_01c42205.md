---
name: crossprovider gemini canonical-source-derived-format-sync-pattern
description: Canonical-source + derived-format sync pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-architecture, validation, consistency]
---

Maintain YAML as authoritative source of truth, auto-generate Markdown from it, and enforce sync checks at pre-commit time to prevent divergence. Applies to any multi-format data representation where human readability requires Markdown but machine parsing needs structure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
